from app.services.connection_manager import ConnectionManager
from app.services.room_service import RoomService

_room_service = RoomService()
_connection_manager = ConnectionManager()


def get_room_service() -> RoomService:
    return _room_service


def get_connection_manager() -> ConnectionManager:
    return _connection_manager
