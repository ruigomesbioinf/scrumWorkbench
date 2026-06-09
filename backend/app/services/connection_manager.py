from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if room_id not in self._connections:
            self._connections[room_id] = []
        self._connections[room_id].append(websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        if room_id in self._connections:
            self._connections[room_id].remove(websocket)
            if not self._connections[room_id]:
                del self._connections[room_id]

    async def broadcast(self, room_id: str, message: dict[str, Any]) -> None:
        for connection in self._connections.get(room_id, []):
            await connection.send_json(message)

    def _get_room_connection_count(self, room_id: str) -> int:
        return len(self._connections.get(room_id, []))
