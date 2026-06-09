from starlette.testclient import TestClient

from app.dependencies import get_connection_manager, get_room_service
from app.main import app
from app.models.deck import DeckType
from app.schemas.ws import OutgoingEventType
from app.services.connection_manager import ConnectionManager
from app.services.room_service import RoomService
from app.testing.builder import BuilderWSMessage


class TestWebSocketConnection:
    def setup_method(self) -> None:
        self.client = TestClient(app)
        self.room_service = RoomService()
        self.connection_manager = ConnectionManager()
        app.dependency_overrides[get_room_service] = lambda: self.room_service
        app.dependency_overrides[get_connection_manager] = lambda: self.connection_manager

    def teardown_method(self) -> None:
        app.dependency_overrides.clear()

    def test_join_broadcasts_player_joined(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            assert data.get("payload", {}).get("username") == ws_join_message.get("payload", {}).get("username")

    def test_join_adds_player_to_room(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            assert len(self.room_service.get_room(room.room_id).players) == 1

    def test_invalid_room_id_returns_error(self) -> None:
        invalid_room_id = "non-existent-room"
        with self.client.websocket_connect(f"/ws/rooms/{invalid_room_id}") as websocket:
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.ERROR
            assert f"Room with ID {invalid_room_id} not found." in data.get("payload", {}).get("error", "")

    def test_first_message_must_be_join(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        invalid_first_message = {"type": "vote", "payload": {}}
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(invalid_first_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.ERROR
            assert "First message must be JOIN" in data.get("payload", {}).get("error", "")

    def test_join_without_username_returns_error(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = {"type": "join", "payload": {}}
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.ERROR
            assert "Username is required to join" in data.get("payload", {}).get("error", "")

    def test_disconnect_marks_player_offline(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            player_id = data.get("payload", {}).get("player_id")
            assert player_id in self.room_service.get_room(room.room_id).players
        assert not self.room_service.get_room(room.room_id).players[player_id].is_connected


class TestWebSocketVoting:
    def setup_method(self) -> None:
        self.client = TestClient(app)
        self.room_service = RoomService()
        self.connection_manager = ConnectionManager()
        app.dependency_overrides[get_room_service] = lambda: self.room_service
        app.dependency_overrides[get_connection_manager] = lambda: self.connection_manager

    def teardown_method(self) -> None:
        app.dependency_overrides.clear()

    def test_vote_sets_player_vote(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_vote_message = BuilderWSMessage.vote_message(DeckType.FIBONACCI)
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            player_id = data.get("payload", {}).get("player_id")
            websocket.send_json(ws_vote_message)
            response = websocket.receive_json()
            assert response.get("type") == OutgoingEventType.VOTE_CAST
            assert self.room_service.get_room(room.room_id).players[player_id].vote == ws_vote_message.get(
                "payload", {}
            ).get("vote")

    def test_vote_broadcasts_vote_cast(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_vote_message = BuilderWSMessage.vote_message(DeckType.FIBONACCI)
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            player_id = data.get("payload", {}).get("player_id")
            websocket.send_json(ws_vote_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.VOTE_CAST
            assert data.get("payload", {}).get("player_id") == player_id

    def test_vote_cast_does_not_include_vote_value(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_vote_message = BuilderWSMessage.vote_message(DeckType.FIBONACCI)
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            websocket.send_json(ws_vote_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.VOTE_CAST
            assert "vote" not in data.get("payload", {})

    def test_invalid_vote_value_returns_error(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        invalid_vote_message = {"type": "vote", "payload": {"vote": "invalid"}}
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            websocket.send_json(invalid_vote_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.ERROR
            assert "Invalid vote value" in data.get("payload", {}).get("error", "")

    def test_vote_without_vote_key_returns_error(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        invalid_vote_message = {"type": "vote", "payload": {}}
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            websocket.send_json(invalid_vote_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.ERROR
            assert "Vote value is required" in data.get("payload", {}).get("error", "")


class TestWebSocketReveal:
    def setup_method(self) -> None:
        self.client = TestClient(app)
        self.room_service = RoomService()
        self.connection_manager = ConnectionManager()
        app.dependency_overrides[get_room_service] = lambda: self.room_service
        app.dependency_overrides[get_connection_manager] = lambda: self.connection_manager

    def teardown_method(self) -> None:
        app.dependency_overrides.clear()

    def test_reveal_broadcasts_votes_revealed(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_reveal_message = BuilderWSMessage.reveal_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            websocket.send_json(ws_reveal_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.VOTE_REVEALED

    def test_revealed_message_contains_player_votes(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_vote_message = BuilderWSMessage.vote_message(DeckType.FIBONACCI)
        ws_reveal_message = BuilderWSMessage.reveal_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            player_id = data.get("payload", {}).get("player_id")
            websocket.send_json(ws_vote_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.VOTE_CAST
            websocket.send_json(ws_reveal_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.VOTE_REVEALED
            votes = data.get("payload", [])
            assert any(
                vote.get("player_id") == player_id
                and vote.get("vote") == ws_vote_message.get("payload", {}).get("vote")
                for vote in votes
            )

    def test_vote_after_reveal_returns_error(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_vote_message = BuilderWSMessage.vote_message(DeckType.FIBONACCI)
        ws_reveal_message = BuilderWSMessage.reveal_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.PLAYER_JOINED
            websocket.send_json(ws_reveal_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.VOTE_REVEALED
            websocket.send_json(ws_vote_message)
            data = websocket.receive_json()
            assert data.get("type") == OutgoingEventType.ERROR
            print(data.get("payload", {}).get("error", ""))
            assert f"Room with ID {room.room_id} is not in voting state. Cannot cast vote." in data.get(
                "payload", {}
            ).get("error", "")


class TestWebSocketReset:
    def setup_method(self) -> None:
        self.client = TestClient(app)
        self.room_service = RoomService()
        self.connection_manager = ConnectionManager()
        app.dependency_overrides[get_room_service] = lambda: self.room_service
        app.dependency_overrides[get_connection_manager] = lambda: self.connection_manager

    def teardown_method(self) -> None:
        app.dependency_overrides.clear()

    def test_reset_broadcasts_vote_reset(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_reset_message = BuilderWSMessage.reset_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data["type"] == OutgoingEventType.PLAYER_JOINED
            websocket.send_json(ws_reset_message)
            data = websocket.receive_json()
            assert data["type"] == OutgoingEventType.VOTE_RESET
            assert data["payload"] == {}

    def test_reset_clears_player_votes(self) -> None:
        room = self.room_service.create_room(DeckType.FIBONACCI)
        ws_join_message = BuilderWSMessage.join_message()
        ws_vote_message = BuilderWSMessage.vote_message(DeckType.FIBONACCI)
        ws_reset_message = BuilderWSMessage.reset_message()
        with self.client.websocket_connect(f"/ws/rooms/{room.room_id}") as websocket:
            websocket.send_json(ws_join_message)
            data = websocket.receive_json()
            assert data["type"] == OutgoingEventType.PLAYER_JOINED
            player_id = data["payload"]["player_id"]
            websocket.send_json(ws_vote_message)
            data = websocket.receive_json()
            assert data["type"] == OutgoingEventType.VOTE_CAST
            websocket.send_json(ws_reset_message)
            data = websocket.receive_json()
            assert data["type"] == OutgoingEventType.VOTE_RESET
            assert self.room_service.get_room(room.room_id).players[player_id].vote is None
