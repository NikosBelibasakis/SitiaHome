from dotenv import load_dotenv
from pydantic import BaseModel, Field
from components.req_and_valid import UserRequirements
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import asyncio, httpx, json, html

load_dotenv()
client = AsyncOpenAI()


# =========================================================
# MODELS
# =========================================================

class PropertyListing(BaseModel):
    title: str = Field(description="Title of the property listing.")
    price: int | None = Field(default=None, description="Monthly rental price in euros.")
    bedrooms: int | None = Field(default=None, description="Number of bedrooms.")
    location: str | None = Field(default=None, description="Location of the property.")
    area_sqm: float | None = Field(default=None, description="Property area in square meters.")
    description: str | None = Field(
        default=None,
        description="A concise paragraph describing the property using the original description and structured property characteristics."
    )
    furnished: bool | None = Field(default=None, description="Whether the property is furnished.")
    url: str = Field(description="Direct URL of the original property listing.")


class PropertyListing_op(BaseModel):
    opinion: str = Field(
        description="A medium-length Greek paragraph giving a balanced assessment of a property, considering both its overall characteristics and how well it matches the user's requirements. Include relevant strengths, weaknesses, and trade-offs."
    )


class FinalProperty(BaseModel):
    property: PropertyListing
    opinion: PropertyListing_op


class PropertySelection(BaseModel):
    urls: list[str]


# =========================================================
# PROPERTY EXTRACTION
# =========================================================

def extract_property_json(html_content: str) -> str | None:
    soup = BeautifulSoup(html_content, "html.parser")
    container = soup.find("div", id="application_container")

    if not container or not (raw_json := container.get("data-json-data")):
        return None

    try:
        property_data = json.loads(html.unescape(raw_json)).get("result")
        return json.dumps(property_data, ensure_ascii=False) if property_data else None
    except json.JSONDecodeError as error:
        print(f"Failed to parse property JSON: {error}")
        return None


async def extract_property_with_llm(property_json: str, url: str) -> PropertyListing | None:
    try:
        response = await client.responses.parse(
            model="gpt-5.4-mini",
            instructions="""
- Carefully inspect all provided property data before assigning values.
- Cross-check information if the same value appears in multiple fields.
- Only assign values supported by the provided property data.
- Do not invent missing information.
- Return null when a value cannot be determined reliably, unless specified otherwise.
- price: monthly rent in euros as an integer.
- bedrooms: number of bedrooms as an integer. If missing or null, return 0.
- location: use the most specific property location available.
- area_sqm: property area in square meters.
- furnished:
  - true if furnished
  - false if unfurnished or not mentioned
- description: concise Greek paragraph using the original listing description and the most important property characteristics.
- url: return exactly the URL provided separately.
""",
            input=f"""
PROPERTY URL:
{url}

PROPERTY DATA:
{property_json}
""",
            text_format=PropertyListing
        )
        return response.output_parsed

    except Exception as error:
        print(f"Failed to extract property from {url}: {error}")
        return None


# =========================================================
# GET DETAILS FOR ALL MATCHING PROPERTIES
# =========================================================

async def get_properties_details(matching_urls: list[str]) -> list[PropertyListing]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=30.0,
        follow_redirects=True
    ) as http_client:

        async def process_property(url: str) -> PropertyListing | None:
            try:
                response = await http_client.get(url)
                response.raise_for_status()

                property_json = extract_property_json(response.text)

                if not property_json:
                    print(f"Property JSON not found for {url}")
                    return None

                return await extract_property_with_llm(property_json, url)

            except httpx.HTTPError as error:
                print(f"Failed to fetch {url}: {error}")
                return None

        results = await asyncio.gather(
            *(process_property(url) for url in matching_urls)
        )

    return [property for property in results if property is not None]


# =========================================================
# RECOMMENDATION / SELECTION
# =========================================================

async def select_properties(
    matching_urls: list[str],
    user_requirements: UserRequirements
) -> list[FinalProperty]:

    properties = await get_properties_details(matching_urls)

    if not properties:
        return []

    async def generate_property_opinion(
        property: PropertyListing
    ) -> FinalProperty | None:

        try:
            response = await client.responses.parse(
                model="gpt-5.4-mini",
                instructions="""
Evaluate the property based on both its characteristics and the user's requirements.

- Write one medium-length paragraph in Greek.
- The opinion may be positive, negative, or mixed.
- Consider the property's strengths, weaknesses, overall characteristics and how well it matches the user's requirements.
- Mention relevant trade-offs when appropriate.
- Base the opinion only on the provided information.
- Do not invent information.
""",
                input=f"""
USER REQUIREMENTS:
{user_requirements.model_dump_json()}

PROPERTY:
{property.model_dump_json()}
""",
                text_format=PropertyListing_op
            )

            return FinalProperty(
                property=property,
                opinion=response.output_parsed
            )

        except Exception as error:
            print(f"Failed to generate opinion for {property.url}: {error}")
            return None

    opinion_results = await asyncio.gather(
        *(generate_property_opinion(property) for property in properties)
    )

    final_properties = [
        property for property in opinion_results
        if property is not None
    ]

    if not final_properties:
        return []

    if len(final_properties) <= 5:
        return final_properties

    properties_text = "\n\n".join(
        property.model_dump_json()
        for property in final_properties
    )

    try:
        response = await client.responses.parse(
            model="gpt-5.4-mini",
            instructions="""
Select and rank the 5 properties that are the best overall matches for the user's requirements.

Consider:
- the property's characteristics
- the user's requirements and preferences
- the assessment already provided for each property

Rank the selected properties from best to worst match.

Rules:
- Select exactly 5 properties.
- Return exactly the URLs of the 5 selected properties.
- Return the URLs in ranked order, with the best match first and the weakest match fifth.
- Use only properties provided in the input.
- Do not invent or modify URLs.
""",
            input=f"""
USER REQUIREMENTS:
{user_requirements.model_dump_json()}

PROPERTIES:
{properties_text}
""",
            text_format=PropertySelection
        )

        properties_by_url = {
            property.property.url: property
            for property in final_properties
        }

        return [
            properties_by_url[url]
            for url in response.output_parsed.urls
            if url in properties_by_url
        ][:5]

    except Exception as error:
        print(f"Failed to select properties: {error}")
        return final_properties[:5]