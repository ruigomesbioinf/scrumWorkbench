from app.decks import get_deck
from app.exceptions import (
    InvalidVoteError,
    PlayerNotFoundError,
    RoomNotFoundError,
    VotingClosedError,
)
from app.models.deck import DeckType, VoteValue
from app.models.rooms import Player, Room, RoomState


class RoomService:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}

    def _get_player(self, room: Room, player_id: str) -> Player:
        player = room.players.get(player_id)
        if not player:
            raise PlayerNotFoundError(player_id, room.room_id)
        return player

    def create_room(self, deck_type: DeckType) -> Room:
        room = Room(deck=get_deck(deck_type))
        self._rooms[room.room_id] = room
        return room

    def get_room(self, room_id: str) -> Room:
        room = self._rooms.get(room_id)
        if not room:
            raise RoomNotFoundError(room_id)
        return room

    def add_player(self, room_id: str, username: str) -> Player:
        room = self.get_room(room_id)
        player = Player(username=username)
        room.players[player.player_id] = player
        return player

    def remove_player(self, room_id: str, player_id: str) -> None:
        room = self.get_room(room_id)
        player = self._get_player(room, player_id)
        player.is_connected = False

    def cast_vote(self, room_id: str, player_id: str, vote_value: VoteValue) -> None:
        room = self.get_room(room_id)

        if room.state != RoomState.VOTING:
            raise VotingClosedError(room_id)

        if vote_value not in room.deck.values:
            raise InvalidVoteError(vote_value, room.deck.deck_type)

        player = self._get_player(room, player_id)
        player.vote = vote_value

    def reveal_votes(self, room_id: str) -> None:
        room = self.get_room(room_id)
        room.state = RoomState.REVEALED

    def reset_round(self, room_id: str) -> None:
        room = self.get_room(room_id)
        room.state = RoomState.VOTING

        for player in room.players.values():
            player.vote = None
