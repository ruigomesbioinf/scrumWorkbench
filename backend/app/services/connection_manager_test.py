from unittest.mock import AsyncMock

from fastapi import WebSocket

from app.services.connection_manager import ConnectionManager
from app.testing.builder import Builder


class TestWebSocketConnect:
    def setup_method(self) -> None:
        self.connection_manager = ConnectionManager()
        self.websocket1 = AsyncMock(spec=WebSocket)
        self.websocket2 = AsyncMock(spec=WebSocket)
        self._room_name1 = Builder.random_string("room")
        self._room_name2 = Builder.random_string("room")

    async def test_increments_connection_count_on_connect(self) -> None:
        await self.connection_manager.connect(self._room_name1, self.websocket1)
        assert self.connection_manager._get_room_connection_count(self._room_name1) == 1

    async def test_accepts_websocket_on_connect(self) -> None:
        await self.connection_manager.connect(self._room_name1, self.websocket1)
        self.websocket1.accept.assert_awaited_once()

    async def test_multiple_connections_to_same_room(self) -> None:
        await self.connection_manager.connect(self._room_name1, self.websocket1)
        await self.connection_manager.connect(self._room_name1, self.websocket2)
        assert self.connection_manager._get_room_connection_count(self._room_name1) == 2

    async def test_connections_are_isolated_by_room(self) -> None:
        await self.connection_manager.connect(self._room_name1, self.websocket1)
        await self.connection_manager.connect(self._room_name2, self.websocket2)
        assert self.connection_manager._get_room_connection_count(self._room_name1) == 1
        assert self.connection_manager._get_room_connection_count(self._room_name2) == 1


class TestWebSocketDisconnect:
    def setup_method(self) -> None:
        self.connection_manager = ConnectionManager()
        self.websocket1 = AsyncMock(spec=WebSocket)
        self.websocket2 = AsyncMock(spec=WebSocket)
        self._room_name = Builder.random_string("room")

    async def test_decrements_connection_count(self) -> None:
        await self.connection_manager.connect(self._room_name, self.websocket1)
        await self.connection_manager.connect(self._room_name, self.websocket2)
        await self.connection_manager.disconnect(self._room_name, self.websocket1)
        assert self.connection_manager._get_room_connection_count(self._room_name) == 1

    async def test_removes_room_key_when_empty(self) -> None:
        await self.connection_manager.connect(self._room_name, self.websocket1)
        await self.connection_manager.disconnect(self._room_name, self.websocket1)
        assert self._room_name not in self.connection_manager._connections

    async def test_disconnect_one_of_many(self) -> None:
        await self.connection_manager.connect(self._room_name, self.websocket1)
        await self.connection_manager.connect(self._room_name, self.websocket2)
        await self.connection_manager.disconnect(self._room_name, self.websocket1)
        assert self.connection_manager._get_room_connection_count(self._room_name) == 1


class TestWebSocketBroadcast:
    def setup_method(self) -> None:
        self.connection_manager = ConnectionManager()
        self.websocket1 = AsyncMock(spec=WebSocket)
        self.websocket2 = AsyncMock(spec=WebSocket)
        self._room_name = Builder.random_string("room")

    async def test_sends_message_to_all_connections(self) -> None:
        await self.connection_manager.connect(self._room_name, self.websocket1)
        await self.connection_manager.connect(self._room_name, self.websocket2)
        message = {"type": "test_message", "content": "Hello, World!"}
        await self.connection_manager.broadcast(self._room_name, message)
        self.websocket1.send_json.assert_awaited_once_with(message)
        self.websocket2.send_json.assert_awaited_once_with(message)

    async def test_broadcast_to_empty_room_does_not_raise(self) -> None:
        message = {"type": "test_message", "content": "Hello, World!"}
        await self.connection_manager.broadcast(self._room_name, message)

    async def test_broadcast_message_content(self) -> None:
        await self.connection_manager.connect(self._room_name, self.websocket1)
        message = {"type": "update", "content": {"key": "value"}}
        await self.connection_manager.broadcast(self._room_name, message)
        self.websocket1.send_json.assert_awaited_once_with(message)
