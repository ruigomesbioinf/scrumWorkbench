from app.models.deck import CardDeck, DeckType

DECKS: dict[DeckType, CardDeck] = {
    DeckType.FIBONACCI: CardDeck(
        deck_type=DeckType.FIBONACCI,
        display_name="Fibonacci",
        values=("1", "2", "3", "5", "8", "13", "21", "?"),
    ),
    DeckType.TIMEBOX: CardDeck(
        deck_type=DeckType.TIMEBOX,
        display_name="Timebox",
        values=("1", "2", "3", "4", "5", "?"),
    ),
    DeckType.TSHIRT: CardDeck(
        deck_type=DeckType.TSHIRT,
        display_name="T-Shirt",
        values=("XS", "S", "M", "L", "XL", "XXL", "?"),
    ),
}


def get_deck(deck_type: DeckType) -> CardDeck:
    """Return the card deck for the given deck type."""
    return DECKS[deck_type]
