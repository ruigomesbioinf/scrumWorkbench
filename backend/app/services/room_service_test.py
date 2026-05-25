import pytest

from app.exceptions import InvalidVoteError, PlayerNotFoundError, RoomNotFoundError, VotingClosedError
from app.models.deck import DeckType
from app.models.rooms import RoomState
from app.services.room_service import RoomService


class TestCreateRoom:
    def setup_method(self) -> None:
        self.room_service = RoomService()

    @pytest.mark.parametrize("deck_type", list(DeckType))
    def test_creates_room_with_correct_deck_types(self, deck_type: DeckType) -> None:
        room = self.room_service.create_room(deck_type)
        assert room.deck.deck_type == deck_type

    def test_creates_room_with_voting_state(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        assert room.state == RoomState.VOTING

    def test_generates_unique_room_ids(self) -> None:
        room1 = self.room_service.create_room(DeckType.FIBONACCI)
        room2 = self.room_service.create_room(DeckType.FIBONACCI)
        assert room1.room_id != room2.room_id


class TestGetRoom:
    def setup_method(self) -> None:
        self.room_service = RoomService()

    def test_get_room_returns_existing_room(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        retrieved_room = self.room_service.get_room(room.room_id)
        assert retrieved_room == room

    def test_get_room_raises_error_for_nonexistent_room(self) -> None:
        with pytest.raises(RoomNotFoundError):
            self.room_service.get_room("nonexistent-room-id")


class TestAddPlayer:
    def setup_method(self) -> None:
        self.room_service = RoomService()
        self.room = self.room_service.create_room(DeckType.FIBONACCI)

    def test_player_added_to_room_players(self) -> None:
        player = self.room_service.add_player(self.room.room_id, "Alice")
        assert player.player_id in self.room.players

    def test_player_keyed_by_player_id(self) -> None:
        player = self.room_service.add_player(self.room.room_id, "Bob")
        assert self.room.players[player.player_id] == player

    def test_player_default_vote_is_none(self) -> None:
        player = self.room_service.add_player(self.room.room_id, "Charlie")
        assert player.vote is None

    def test_player_is_connected_by_default(self) -> None:
        player = self.room_service.add_player(self.room.room_id, "Dave")
        assert player.is_connected is True

    def test_raises_for_nonexistent_room(self) -> None:
        with pytest.raises(RoomNotFoundError):
            self.room_service.add_player("nonexistent-room-id", "Eve")


class TestRemovePlayer:
    def setup_method(self) -> None:
        self.room_service = RoomService()
        self.room = self.room_service.create_room(DeckType.FIBONACCI)
        self.player = self.room_service.add_player(self.room.room_id, "Alice")

    def test_player_marked_as_disconnected(self) -> None:
        self.room_service.remove_player(self.room.room_id, self.player.player_id)
        assert not self.player.is_connected

    def test_player_remains_in_room_after_disconnection(self) -> None:
        self.room_service.remove_player(self.room.room_id, self.player.player_id)
        assert self.player.player_id in self.room.players

    def test_vote_preserved_after_disconnection(self) -> None:
        self.player.vote = "5"
        self.room_service.remove_player(self.room.room_id, self.player.player_id)
        assert self.player.vote == "5"

    def test_raises_for_unknown_room_id(self) -> None:
        with pytest.raises(RoomNotFoundError):
            self.room_service.remove_player("nonexistent-room-id", self.player.player_id)

    def test_raises_for_unknown_player_id(self) -> None:
        with pytest.raises(PlayerNotFoundError):
            self.room_service.remove_player(self.room.room_id, "nonexistent-player-id")


class TestCastVote:
    def setup_method(self) -> None:
        self.room_service = RoomService()
        self.room = self.room_service.create_room(DeckType.FIBONACCI)
        self.player = self.room_service.add_player(self.room.room_id, "Alice")

    def test_set_player_vote(self) -> None:
        self.room_service.cast_vote(self.room.room_id, self.player.player_id, "5")
        assert self.player.vote == "5"

    def test_raises_for_value_not_in_deck(self) -> None:
        with pytest.raises(InvalidVoteError):
            self.room_service.cast_vote(self.room.room_id, self.player.player_id, "invalid-vote")

    def test_raises_when_voting_is_closed(self) -> None:
        self.room_service.reveal_votes(self.room.room_id)
        with pytest.raises(VotingClosedError):
            self.room_service.cast_vote(self.room.room_id, self.player.player_id, "5")

    def test_raises_for_unknown_room_id(self) -> None:
        with pytest.raises(RoomNotFoundError):
            self.room_service.cast_vote("nonexistent-room-id", self.player.player_id, "5")

    def test_raises_for_unknown_player_id(self) -> None:
        with pytest.raises(PlayerNotFoundError):
            self.room_service.cast_vote(self.room.room_id, "nonexistent-player-id", "5")

    @pytest.mark.parametrize(
        "deck_type, valid_vote",
        [
            (DeckType.FIBONACCI, "5"),
            (DeckType.TIMEBOX, "1"),
            (DeckType.TSHIRT, "M"),
        ],
    )
    def test_valid_vote_on_each_deck_type(self, deck_type: DeckType, valid_vote: str) -> None:
        room = self.room_service.create_room(deck_type)
        player = self.room_service.add_player(room.room_id, "Bob")
        self.room_service.cast_vote(room.room_id, player.player_id, valid_vote)
        assert player.vote == valid_vote


class TestRevealVotes:
    def setup_method(self) -> None:
        self.room_service = RoomService()
        self.room = self.room_service.create_room(DeckType.FIBONACCI)

    def test_states_becomes_revealed(self) -> None:
        self.room_service.reveal_votes(self.room.room_id)
        assert self.room.state == RoomState.REVEALED

    def test_raises_for_unknown_room_id(self) -> None:
        with pytest.raises(RoomNotFoundError):
            self.room_service.reveal_votes("nonexistent-room-id")


class TestResetRound:
    def setup_method(self) -> None:
        self.room_service = RoomService()
        self.room = self.room_service.create_room(DeckType.FIBONACCI)

    def test_all_votes_cleared(self) -> None:
        player1 = self.room_service.add_player(self.room.room_id, "Alice")
        player2 = self.room_service.add_player(self.room.room_id, "Bob")
        self.room_service.cast_vote(self.room.room_id, player1.player_id, "5")
        self.room_service.cast_vote(self.room.room_id, player2.player_id, "8")
        self.room_service.reset_round(self.room.room_id)
        assert player1.vote is None
        assert player2.vote is None

    def test_disconnected_player_vote_also_cleared(self) -> None:
        player = self.room_service.add_player(self.room.room_id, "Charlie")
        self.room_service.cast_vote(self.room.room_id, player.player_id, "3")
        self.room_service.remove_player(self.room.room_id, player.player_id)
        self.room_service.reset_round(self.room.room_id)
        assert player.vote is None

    def test_state_returns_to_voting(self) -> None:
        self.room_service.reveal_votes(self.room.room_id)
        self.room_service.reset_round(self.room.room_id)
        assert self.room.state == RoomState.VOTING

    def test_raises_for_unknown_room_id(self) -> None:
        with pytest.raises(RoomNotFoundError):
            self.room_service.reset_round("nonexistent-room-id")
