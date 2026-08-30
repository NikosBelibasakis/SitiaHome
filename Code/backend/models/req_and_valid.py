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
        description="Minimum monthly rent in euros specified by the user."
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
You are the User Requirements Processing and Validation component of SitiaHome, an application for finding long-term rental properties in the Municipality of Sitia, Crete.

Your task is to analyze the user's natural-language request and return the required structured output. Extract the minimum monthly rent as min_rent, the maximum monthly rent as max_rent, and the minimum required number of bedrooms as min_bedrooms.

The fields min_rent, max_rent, and min_bedrooms are required user requirements. The user must explicitly provide a value for each required field, unless a specific exception is defined below. If a required value cannot be identified from the user's request, return null for the corresponding field. Never invent, assume, or infer missing values.

For min_rent, the user must either explicitly provide a minimum rent value or explicitly state that they do not care about the minimum rent or that there is no lower rent limit. Only in that case, set min_rent to 0.

Do not infer min_rent from expressions that only specify a maximum rent, such as "up to 500 euros", "maximum 500 euros", "no more than 500 euros", or similar phrases. If only a maximum rent is provided and the user does not explicitly provide or address the minimum rent, return null for min_rent.

Any other explicitly mentioned housing preferences or requirements must be placed in additional_information as short, separate bullet-style items. This field is optional. If no additional preferences are mentioned, return null for additional_information.

At the same time, determine whether the user's request is valid. Set legit_prompt to false if the request is not about finding a property for long-term rental in the Municipality of Sitia, if any of the required fields min_rent, max_rent, or min_bedrooms is missing, or if any required value is logically invalid or unreasonable.

A rent value is invalid if it is negative or if max_rent is lower than min_rent. For min_bedrooms, only integer values from 0 to 9 inclusive are considered valid. Any value below 0 or greater than 9 is invalid.

If the user specifies a number of bedrooms without explicitly using terms such as "minimum" or "at least", interpret that number as min_bedrooms. If no number of bedrooms is provided, return null for min_bedrooms.

If the user does not explicitly mention a location, assume that the request concerns the Municipality of Sitia. Only consider the location invalid if the user explicitly requests a property outside the Municipality of Sitia.

Likewise, assume that the request concerns long-term rental unless the user explicitly requests short-term accommodation.

If legit_prompt is true, set validation_message to "OK". If legit_prompt is false, set validation_message to a short, clear, one-sentence explanation of why the request is invalid.

Always write validation_message in Greek, regardless of the language used by the user.
"""


def process_and_validate_requirements(user_prompt: str) -> UserRequirements:
    response = client.responses.parse(
        model= "gpt-5.6-luna",
        instructions= REQUIREMENTS_PROCESSING_AND_VALIDATION_LLM_SYSTEM_PROMPT,
        input= user_prompt,
        text_format= UserRequirements,
    )

    return response.output_parsed