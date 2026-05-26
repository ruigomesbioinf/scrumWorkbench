from pydantic import BaseModel

from app.models.deck import DeckType, VoteValue
from app.models.rooms import Room, RoomState


class CreateRoomRequest(BaseModel):
    deck_type: DeckType


class PlayerResponse(BaseModel):
    player_id: str
    username: str
    vote: VoteValue | None
    is_connected: bool


class RoomResponse(BaseModel):
    room_id: str
    deck_type: DeckType
    deck_display_name: str
    deck_values: tuple[VoteValue, ...]
    state: RoomState
    players: dict[str, PlayerResponse]

    @classmethod
    def from_room(cls, room: Room) -> "RoomResponse":
        return cls(
            room_id=room.room_id,
            deck_type=room.deck.deck_type,
            deck_display_name=room.deck.display_name,
            deck_values=room.deck.values,
            state=room.state,
            players={
                player_id: PlayerResponse(
                    player_id=player.player_id,
                    username=player.username,
                    vote=player.vote,
                    is_connected=player.is_connected,
                )
                for player_id, player in room.players.items()
            },
        )
