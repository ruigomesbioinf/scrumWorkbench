import pytest
from pydantic import ValidationError

from app.models.deck import DeckType
from app.testing.builder import Builder


class TestDeckType:
    def test_deck_type_number_of_members(self) -> None:
        assert len(DeckType) == 3

    def test_deck_type_member_values(self) -> None:
        assert DeckType.FIBONACCI.value == "fibonacci"
        assert DeckType.TIMEBOX.value == "timebox"
        assert DeckType.TSHIRT.value == "tshirt"

    def test_deck_types_have_valid_string_values(self) -> None:
        for deck_type in DeckType:
            assert isinstance(deck_type.value, str)
            assert deck_type.value in {"fibonacci", "timebox", "tshirt"}


class TestCardDeck:
    def test_card_deck_valid_constructor(self) -> None:
        deck_display_name = Builder.random_string("Deck")
        deck_values = Builder.random_list_of_string_numbers(7)

        deck = Builder.build_random_card_deck(
            deck_type=DeckType.FIBONACCI,
            display_name=deck_display_name,
            values=deck_values,
        )

        assert deck.deck_type == DeckType.FIBONACCI
        assert deck.display_name == deck_display_name
        assert deck.values == deck_values

    def test_frozen_deck_type_raises_error_on_mutation(self) -> None:
        deck = Builder.build_random_card_deck()

        with pytest.raises(ValidationError):
            deck.deck_type = DeckType.TIMEBOX

    def test_frozen_values_raises_error_on_mutation(self) -> None:
        deck = Builder.build_random_card_deck()

        with pytest.raises(ValidationError):
            deck.values += ("34",)

    def test_empty_values_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            Builder.build_random_card_deck(values=())

    def test_single_value_in_values_is_valid(self) -> None:
        deck = Builder.build_random_card_deck(values=("1",))
        assert deck.values == ("1",)

    def test_values_preserves_order(self) -> None:
        custom_values = ("5", "3", "8", "1", "2")
        deck = Builder.build_random_card_deck(values=custom_values)
        assert deck.values == custom_values

    def test_display_name_is_stored_correctly(self) -> None:
        display_name = Builder.random_string("DisplayName")
        deck = Builder.build_random_card_deck(display_name=display_name)
        assert deck.display_name == display_name
