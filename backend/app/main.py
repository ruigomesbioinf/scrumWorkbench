from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class HealthCheckResponse(BaseModel):
    status: str = "OK"


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World, welcome to life!"}


@app.get(
    "/health",
    tags=["health_check"],
    summary="Perform an application health check",
    response_description="Health check response indicating the status of the application via status code",
    status_code=200,
    response_model=HealthCheckResponse,
)
async def health() -> HealthCheckResponse:
    return HealthCheckResponse(status="ok")
