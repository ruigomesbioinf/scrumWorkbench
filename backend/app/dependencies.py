from app.services.room_service import RoomService

_room_service = RoomService()


def get_room_service() -> RoomService:
    return _room_service
