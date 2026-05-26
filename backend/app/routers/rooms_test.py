import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_room_service
from app.main import app
from app.models.deck import DeckType
from app.services.room_service import RoomService


class TestCreateRoom:
    def setup_method(self) -> None:
        self.room_service = RoomService()
        app.dependency_overrides[get_room_service] = lambda: self.room_service

    def teardown_method(self) -> None:
        app.dependency_overrides.clear()

    async def test_create_room_returns_201_with_room_data(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post("/rooms", json={"deck_type": "fibonacci"})
            assert response.status_code == 201
            assert "room_id" in response.json()

    @pytest.mark.parametrize("deck_type", list(DeckType))
    async def test_returns_correct_deck_type(self, deck_type: DeckType) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post("/rooms", json={"deck_type": deck_type.value})
            assert response.status_code == 201
            assert response.json()["deck_type"] == deck_type.value

    async def test_invalid_deck_type_returns_422(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post("/rooms", json={"deck_type": "invalid-deck"})
            assert response.status_code == 422

    async def test_room_has_voting_state(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post("/rooms", json={"deck_type": "fibonacci"})
            assert response.status_code == 201
            assert response.json()["state"] == "voting"
