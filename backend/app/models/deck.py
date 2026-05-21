from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeckType(StrEnum):
    FIBONACCI = "fibonacci"
    TIMEBOX = "timebox"
    TSHIRT = "tshirt"


type VoteValue = str


class CardDeck(BaseModel):
    model_config = ConfigDict(frozen=True)

    deck_type: Annotated[
        DeckType,
        Field(description="The type of the card deck, which determines the set of possible vote values."),
    ]

    display_name: Annotated[
        str,
        Field(description="A human-readable name for the card deck, used for display purposes."),
    ]

    values: Annotated[
        tuple[VoteValue, ...],
        Field(description="A list of possible vote values that can be used with this card deck."),
    ]

    @field_validator("values")
    @classmethod
    def validate_values_not_empty(cls, values: tuple[VoteValue, ...]) -> tuple[VoteValue, ...]:
        if not values:
            raise ValueError("The 'values' field must contain at least one vote value.")
        return values
