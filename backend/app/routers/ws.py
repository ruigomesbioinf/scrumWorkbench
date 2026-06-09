from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.dependencies import get_connection_manager, get_room_service
from app.exceptions import ScrumWorkbenchError
from app.models.rooms import Player
from app.schemas.ws import (
    IncomingEventType,
    IncomingMessage,
    all_votes_revealed_message,
    error_message,
    player_joined_message,
    player_left_message,
    vote_cast_message,
    vote_reset_message,
)
from app.services.connection_manager import ConnectionManager
from app.services.room_service import RoomService

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


@dataclass
class SessionContext:
    room_id: str
    player: Player
    room_service: RoomService
    connection_manager: ConnectionManager
    websocket: WebSocket


async def _handle_join(
    room_id: str,
    websocket: WebSocket,
    room_service: RoomService,
    connection_manager: ConnectionManager,
) -> Player | None:
    try:
        message = IncomingMessage.model_validate(await websocket.receive_json())
    except ValidationError:
        await websocket.send_json(error_message("Invalid message format"))
        raise

    if message.type != IncomingEventType.JOIN:
        await websocket.send_json(error_message("First message must be JOIN"))
        return None

    username = message.payload.get("username")
    if not username:
        await websocket.send_json(error_message("Username is required to join"))
        return None

    player = room_service.add_player(room_id, username)
    await connection_manager.broadcast(room_id, player_joined_message(player))
    return player


async def _handle_vote(ctx: SessionContext, payload: dict[str, Any]) -> None:
    vote = payload.get("vote")
    if vote is None:
        await ctx.websocket.send_json(error_message("Vote value is required"))
        return
    ctx.room_service.cast_vote(ctx.room_id, ctx.player.player_id, vote)
    await ctx.connection_manager.broadcast(ctx.room_id, vote_cast_message(ctx.player))


async def _handle_reveal(ctx: SessionContext) -> None:
    ctx.room_service.reveal_votes(ctx.room_id)
    room = ctx.room_service.get_room(ctx.room_id)
    await ctx.connection_manager.broadcast(ctx.room_id, all_votes_revealed_message(room))


async def _handle_reset(ctx: SessionContext) -> None:
    ctx.room_service.reset_round(ctx.room_id)
    await ctx.connection_manager.broadcast(ctx.room_id, vote_reset_message())


async def _dispatch(ctx: SessionContext, message: IncomingMessage) -> None:
    match message.type:
        case IncomingEventType.VOTE:
            await _handle_vote(ctx, message.payload)
        case IncomingEventType.REVEAL:
            await _handle_reveal(ctx)
        case IncomingEventType.RESET:
            await _handle_reset(ctx)
        case IncomingEventType.JOIN:
            await ctx.websocket.send_json(error_message("Already joined"))


async def _run_session_loop(ctx: SessionContext) -> None:
    while True:
        try:
            message = IncomingMessage.model_validate(await ctx.websocket.receive_json())
        except ValidationError:
            await ctx.websocket.send_json(error_message("Invalid message format"))
            continue

        try:
            await _dispatch(ctx, message)
        except ScrumWorkbenchError as exc:
            await ctx.websocket.send_json(error_message(str(exc)))


@ws_router.websocket("/rooms/{room_id}")
async def websocket_endpoint(
    room_id: str,
    websocket: WebSocket,
    room_service: Annotated[RoomService, Depends(get_room_service)],
    connection_manager: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> None:
    player: Player | None = None

    try:
        await connection_manager.connect(room_id, websocket)
        room_service.get_room(room_id)
        player = await _handle_join(room_id, websocket, room_service, connection_manager)
        if player is None:
            return
        ctx = SessionContext(room_id, player, room_service, connection_manager, websocket)
        await _run_session_loop(ctx)

    except ScrumWorkbenchError as exc:
        await websocket.send_json(error_message(str(exc)))

    except WebSocketDisconnect:
        pass

    finally:
        await connection_manager.disconnect(room_id, websocket)
        if player is not None:
            try:
                room_service.remove_player(room_id, player.player_id)
                await connection_manager.broadcast(room_id, player_left_message(player))
            except ScrumWorkbenchError:
                pass
