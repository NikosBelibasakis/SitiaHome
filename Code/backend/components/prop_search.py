import html
import json
import httpx
from bs4 import BeautifulSoup
from components.req_and_valid import UserRequirements


XE_RESULTS_URL = (
    "https://www.xe.gr/property/results"
    "?transaction_name=rent"
    "&item_type=residence"
    "&country=GR"
    "&geo_lat_from=35.318250464475454"
    "&geo_lng_from=26.413911886840907"
    "&geo_lat_to=34.96539707477967"
    "&geo_lng_to=25.887300874485817"
)


def fetch_xe_json():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        )
    }

    response = httpx.get(
        XE_RESULTS_URL,
        headers=headers,
        follow_redirects=True,
        timeout=30.0,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div",id="application_container")
    raw_json = container.get("data-json-data")
    decoded_json = html.unescape(raw_json)
    data = json.loads(decoded_json)

    return data


def parse_price(price: str) -> int:
    return int(
        price
        .replace("€", "")
        .replace("\xa0", "")
        .replace(".", "")
        .strip()
    )


def filter_xe_listings(data: dict, requirements: UserRequirements,) -> list[str]:

    matching_urls = []

    for listing in data["results"]:
        price = parse_price(listing["price"])
        bedrooms = listing["bedrooms"]

        if bedrooms is None:
            bedrooms = 0

        if (
            requirements.min_rent <= price <= requirements.max_rent
            and bedrooms >= requirements.min_bedrooms
        ):
            matching_urls.append(listing["url"])

    return matching_urls


def search_xe_properties(requirements: UserRequirements,) -> list[str]:

    data = fetch_xe_json()

    matching_urls = filter_xe_listings(data,requirements)

    return matching_urls 