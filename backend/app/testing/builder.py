import random
import uuid

from app.models.deck import CardDeck, DeckType


class Builder:
    @staticmethod
    def random_string(prefix: str = "value") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def random_list_of_string_numbers(length: int = 5) -> tuple[str, ...]:
        return tuple(str(random.randint(1, 100)) for _ in range(length))

    @staticmethod
    def random_deck_type() -> DeckType:
        return random.choice(list(DeckType))

    @staticmethod
    def build_random_card_deck(
        *,
        deck_type: DeckType | None = None,
        display_name: str | None = None,
        values: tuple[str, ...] | None = None,
    ) -> CardDeck:
        resolved_deck_type = deck_type or Builder.random_deck_type()

        return CardDeck(
            deck_type=resolved_deck_type,
            display_name=display_name or Builder.random_string("Deck"),
            values=values if values is not None else ("1", "2", "3", "5", "8", "13", "21"),
        )


class BuildPlayer:
    @staticmethod
    def build_random_player(
        *,
        player_id: str | None = None,
        username: str | None = None,
        vote: str | None = None,
        is_connected: bool = True,
    ) -> dict[str, object]:
        return {
            "player_id": player_id or str(uuid.uuid4()),
            "username": username or Builder.random_string("Player"),
            "vote": vote,
            "is_connected": is_connected,
        }

    @staticmethod
    def default_player() -> dict[str, object]:
        return {
            "player_id": str(uuid.uuid4()),
            "username": Builder.random_string("Player"),
            "vote": None,
            "is_connected": True,
        }

    @staticmethod
    def voted_player(vote: str) -> dict[str, object]:
        return {
            "player_id": str(uuid.uuid4()),
            "username": Builder.random_string("Player"),
            "vote": vote,
            "is_connected": True,
        }

    @staticmethod
    def disconnected_player() -> dict[str, object]:
        return {
            "player_id": str(uuid.uuid4()),
            "username": Builder.random_string("Player"),
            "vote": None,
            "is_connected": False,
        }


class BuildRoom:
    @staticmethod
    def build_random_room(
        *,
        room_id: str | None = None,
        deck: CardDeck | None = None,
        state: str = "voting",
        players: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return {
            "room_id": room_id or str(uuid.uuid4()),
            "deck": deck or Builder.build_random_card_deck(),
            "state": state,
            "players": players or {},
        }

    @staticmethod
    def default_room() -> dict[str, object]:
        return {
            "room_id": str(uuid.uuid4()),
            "deck": Builder.build_random_card_deck(),
            "state": "voting",
            "players": {},
        }

    @staticmethod
    def room_with_players(num_players: int = 3) -> dict[str, object]:
        players = {BuildPlayer.build_random_player() for _ in range(num_players)}
        return {
            "room_id": str(uuid.uuid4()),
            "deck": Builder.build_random_card_deck(),
            "state": "voting",
            "players": players,
        }

    @staticmethod
    def revealed_room_with_players(num_players: int = 3) -> dict[str, object]:
        players = {BuildPlayer.build_random_player() for _ in range(num_players)}
        return {
            "room_id": str(uuid.uuid4()),
            "deck": Builder.build_random_card_deck(),
            "state": "revealed",
            "players": players,
        }
