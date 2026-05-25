import pytest
from pydantic import ValidationError

from app.models.rooms import Player, Room, RoomState
from app.testing.builder import Builder


class TestRoomState:
    def test_has_exactly_two_states(self) -> None:
        assert len(RoomState) == 2

    def test_voting_serializes_to_string(self) -> None:
        assert RoomState.VOTING.value == "voting"

    def test_revealed_serializes_to_string(self) -> None:
        assert RoomState.REVEALED.value == "revealed"


class TestPlayer:
    def test_generates_unique_player_ids(self) -> None:
        player1 = Player(username="John")
        player2 = Player(username="Jane")
        assert player1.player_id != player2.player_id

    def test_default_player_vote_is_none(self) -> None:
        player = Player(username="John")
        assert player.vote is None

    def test_default_player_is_connected(self) -> None:
        player = Player(username="John")
        assert player.is_connected is True

    def test_empty_username_is_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Player(username="")

    def test_username_too_long_is_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Player(username="a" * 21)

    def test_vote_can_be_mutated(self) -> None:
        player = Player(username="John")
        player.vote = "5"
        assert player.vote == "5"


class TestRoom:
    def test_generates_unique_room_ids(self) -> None:
        room1 = Room(deck=Builder.build_random_card_deck())
        room2 = Room(deck=Builder.build_random_card_deck())
        assert room1.room_id != room2.room_id

    def test_default_room_state_is_voting(self) -> None:
        room = Room(deck=Builder.build_random_card_deck())
        assert room.state == RoomState.VOTING

    def test_default_players_is_empty_dict(self) -> None:
        room = Room(deck=Builder.build_random_card_deck())
        assert room.players == {}

    def test_players_can_be_added_to_room(self) -> None:
        room = Room(deck=Builder.build_random_card_deck())
        player = Player(username="John")
        room.players[player.player_id] = player
        assert player.player_id in room.players
