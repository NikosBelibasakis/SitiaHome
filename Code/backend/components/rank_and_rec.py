from pydantic import BaseModel, Field
from prop_search import search_xe_properties
from req_and_valid import UserRequirements


class PropertyListing(BaseModel):
    title: str = Field(
        description="Title of the property listing."
    )

    price: int | None = Field(
        default=None,
        description="Monthly rental price in euros."
    )

    bedrooms: int | None = Field(
        default=None,
        description="Number of bedrooms."
    )

    location: str | None = Field(
        default=None,
        description="Location of the property."
    )

    area_sqm: float | None = Field(
        default=None,
        description="Property area in square meters."
    )

    description: str | None = Field(
        default=None,
        description=(
            "A concise paragraph describing the property, generated from both "
            "the original description provided on the listing website and the "
            "structured property characteristics available on the listing page."
        )
    )

    furnished: bool | None = Field(
        default=None,
        description="Whether the property is furnished."
    )

    url: str = Field(
        description="Direct URL of the original property listing."
    )


urls = search_xe_properties(requirements)