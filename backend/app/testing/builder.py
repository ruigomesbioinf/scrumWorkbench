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
