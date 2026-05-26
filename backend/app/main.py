from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import InvalidVoteError, PlayerNotFoundError, RoomNotFoundError, VotingClosedError
from app.routers.rooms import room_router

app = FastAPI()
app.include_router(room_router)


@app.exception_handler(RoomNotFoundError)
def room_not_found_exception_handler(request: Request, exc: RoomNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


@app.exception_handler(PlayerNotFoundError)
def player_not_found_exception_handler(request: Request, exc: PlayerNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


@app.exception_handler(InvalidVoteError)
def invalid_vote_exception_handler(request: Request, exc: InvalidVoteError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message},
    )


@app.exception_handler(VotingClosedError)
def voting_closed_exception_handler(request: Request, exc: VotingClosedError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message},
    )
