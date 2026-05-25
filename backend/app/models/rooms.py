import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.deck import CardDeck, VoteValue


class RoomState(Enum):
    VOTING = "voting"
    REVEALED = "revealed"


class Player(BaseModel):
    model_config = ConfigDict(frozen=False)

    player_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the player, generated as a UUID string.",
    )

    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="The player's username, which must be between 3 and 20 characters long.",
    )

    vote: VoteValue | None = Field(
        default=None,
        description="The player's current vote, which can be a string value or None if the player has not voted yet.",
    )

    is_connected: bool = Field(
        default=True,
        description="Indicates whether the player is currently connected to the room.",
    )


class Room(BaseModel):
    model_config = ConfigDict(frozen=False)

    room_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the room, generated as a UUID string.",
    )

    deck: CardDeck = Field(
        ...,
        description="The card deck being used in the room, which determines the possible vote values.",
    )

    state: RoomState = Field(
        default=RoomState.VOTING,
        description="The current state of the room, which can be either 'voting' or 'revealed'.",
    )

    players: dict[str, Player] = Field(
        default_factory=dict,
        description="A list of players currently in the room.",
    )
