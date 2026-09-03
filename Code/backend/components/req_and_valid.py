from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI()


class UserRequirements(BaseModel):
    legit_prompt: bool = Field(
        description="Whether the user's request is valid according to the SitiaHome requirements."
    )

    min_rent: int | None = Field(
        default=None,
        description="Optional minimum monthly rent in euros. Return null if the user does not specify a minimum rent."
    )

    max_rent: int | None = Field(
        default=None,
        description="Maximum monthly rent in euros specified by the user."
    )

    min_bedrooms: int | None = Field(
        default=None,
        description="Minimum number of bedrooms required by the user."
    )

    additional_information: str | None = Field(
        default=None,
        description="Any additional property preferences explicitly mentioned by the user."
    )

    validation_message: str = Field(
        description="Short explanation of the validation result. Returns 'OK' when the request is valid."
    )


REQUIREMENTS_PROCESSING_AND_VALIDATION_LLM_SYSTEM_PROMPT = """
You are the User Requirements Processing and Validation component of SitiaHome.

Analyze the user's request and return the structured output.

Required fields:
- max_rent
- min_bedrooms

Rules:
- If the user gives a rent range, use the lower value as min_rent and the upper value as max_rent.
- If no minimum rent is specified, return null for min_rent.
- If max_rent is missing, return null.
- If min_bedrooms is missing, return null.
- Do not invent missing values.
- Put any other housing preferences in additional_information. Return null if none are provided.
- Do not repeat min_rent, max_rent, or min_bedrooms in additional_information.

Set legit_prompt to false if:
- max_rent or min_bedrooms is missing,
- the request is not for long-term rental in the Municipality of Sitia,
- or a provided value is invalid.

The absence of min_rent must not make the request invalid.

Rent values cannot be negative. If min_rent is provided, max_rent cannot be lower than min_rent.

min_bedrooms must be an integer from 0 to 9.
If the user requests a studio/garsoniera or states that no bedroom is required, set min_bedrooms to 0.

If no location is specified, assume the Municipality of Sitia.
If no rental duration is specified, assume long-term rental.

If legit_prompt is true, set validation_message to "OK".
Otherwise, return a short validation message in Greek.
"""


def process_and_validate_requirements(user_prompt: str) -> UserRequirements:
    response = client.responses.parse(
        model= "gpt-5.6-luna",
        instructions= REQUIREMENTS_PROCESSING_AND_VALIDATION_LLM_SYSTEM_PROMPT,
        input= user_prompt,
        text_format= UserRequirements,
    )

    return response.output_parsed