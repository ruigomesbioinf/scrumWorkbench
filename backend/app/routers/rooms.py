from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_room_service
from app.schemas.room import CreateRoomRequest, RoomResponse
from app.services.room_service import RoomService

room_router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
)


@room_router.post(
    "",
    summary="Create a new planning poker room",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    body: CreateRoomRequest,
    room_service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    room = room_service.create_room(body.deck_type)
    return RoomResponse.from_room(room)


@room_router.get(
    "/{room_id}",
    summary="Get details of a planning poker room",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
)
def get_room(
    room_id: str,
    room_service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    room = room_service.get_room(room_id)
    return RoomResponse.from_room(room)
