from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.models.rooms import Player, Room


class IncomingEventType(StrEnum):
    JOIN = "join"
    VOTE = "vote"
    REVEAL = "reveal"
    RESET = "reset"


class OutgoingEventType(StrEnum):
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    VOTE_CAST = "vote_cast"
    VOTE_REVEALED = "vote_revealed"
    VOTE_RESET = "vote_reset"
    ROOM_RESET = "room_reset"
    ERROR = "error"


class IncomingMessage(BaseModel):
    type: IncomingEventType
    payload: dict[str, Any] = Field(default_factory=dict)


def player_joined_message(player: Player) -> dict[str, Any]:
    return {
        "type": OutgoingEventType.PLAYER_JOINED,
        "payload": {
            "player_id": player.player_id,
            "username": player.username,
        },
    }


def player_left_message(player: Player) -> dict[str, Any]:
    return {
        "type": OutgoingEventType.PLAYER_LEFT,
        "payload": {
            "player_id": player.player_id,
            "username": player.username,
        },
    }


def vote_cast_message(player: Player) -> dict[str, Any]:
    return {
        "type": OutgoingEventType.VOTE_CAST,
        "payload": {
            "player_id": player.player_id,
            "username": player.username,
        },
    }


def all_votes_revealed_message(room: Room) -> dict[str, Any]:
    return {
        "type": OutgoingEventType.VOTE_REVEALED,
        "payload": [
            {
                "player_id": player.player_id,
                "username": player.username,
                "vote": player.vote,
            }
            for player in room.players.values()
        ],
    }


def vote_reset_message() -> dict[str, Any]:
    return {"type": OutgoingEventType.VOTE_RESET, "payload": {}}


def error_message(error: str) -> dict[str, Any]:
    return {"type": OutgoingEventType.ERROR, "payload": {"error": error}}
