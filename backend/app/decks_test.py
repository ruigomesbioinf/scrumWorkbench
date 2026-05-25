import pytest

from app.decks import DECKS, get_deck
from app.models.deck import DeckType


class TestGetDeck:
    @pytest.mark.parametrize(
        "deck_type, expected_values",
        [
            (DeckType.FIBONACCI, DeckType.FIBONACCI.value),
            (DeckType.TIMEBOX, DeckType.TIMEBOX.value),
            (DeckType.TSHIRT, DeckType.TSHIRT.value),
        ],
    )
    def test_returns_correct_deck_type(self, deck_type: DeckType, expected_values: str) -> None:
        deck = get_deck(deck_type=deck_type)
        assert deck.deck_type == expected_values

    @pytest.mark.parametrize(
        "deck_type, display_name",
        [
            (DeckType.FIBONACCI, "Fibonacci"),
            (DeckType.TIMEBOX, "Timebox"),
            (DeckType.TSHIRT, "T-Shirt"),
        ],
    )
    def test_returns_correct_display_name(self, deck_type: DeckType, display_name: str) -> None:
        deck = get_deck(deck_type=deck_type)
        assert deck.display_name == display_name

    def test_all_deck_types_are_covered(self) -> None:
        assert len(DECKS) == len(DeckType)


class TestDeckValues:
    @pytest.mark.parametrize("deck_type", list(DeckType))
    def test_no_deck_has_duplicate_values(self, deck_type: DeckType) -> None:
        deck = get_deck(deck_type=deck_type)
        assert len(deck.values) == len(set(deck.values)), f"Deck {deck.display_name} has duplicate values"

    @pytest.mark.parametrize("deck_type", list(DeckType))
    def test_every_deck_contains_unknown_card(self, deck_type: DeckType) -> None:
        deck = get_deck(deck_type=deck_type)
        assert "?" in deck.values, f"Deck {deck.display_name} does not contain an unknown card"

    @pytest.mark.parametrize("deck_type", [DeckType.FIBONACCI, DeckType.TIMEBOX])
    def test_fibonnaci_timebox_numeric_values_are_valid_integers(self, deck_type: DeckType) -> None:
        deck = get_deck(deck_type=deck_type)
        numeric_values = [value for value in deck.values if value != "?"]
        for value in numeric_values:
            assert value.isdigit(), f"Deck {deck.display_name} contains non-numeric value: {value}"

    def test_tshirt_values_are_uppercase_alphabetic(self) -> None:
        deck = get_deck(deck_type=DeckType.TSHIRT)
        values = [value for value in deck.values if value != "?"]
        for value in values:
            assert value.isalpha() and value.isupper(), (
                f"Deck {deck.display_name} contains invalid T-Shirt size: {value}"
            )
