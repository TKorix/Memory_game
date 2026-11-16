"""board.py - a Board osztály: a kártyapár-kereső játékpályája."""
import random

from card import Card


class Board:
    """A pálya: létrehozza a kártyapárokat, megkeveri őket, és tudja, mikor van vége."""

    def __init__(self, rows: int, cols: int, symbols: list[str]) -> None:
        if (rows * cols) % 2 != 0:
            raise ValueError("A kártyák számának párosnak kell lennie.")
        pairs = rows * cols // 2
        if len(symbols) < pairs:
            raise ValueError("Nincs elég szimbólum a pályához.")

        self.rows: int = rows
        self.cols: int = cols
        self.cards: list[Card] = []

        # Véletlenszerűen kiválasztunk annyi szimbólumot, ahány pár kell,
        # és mindegyikhez két kártyát készítünk.
        for symbol in random.sample(symbols, pairs):
            self.cards.append(Card(symbol))
            self.cards.append(Card(symbol))
        self.shuffle()

    def shuffle(self) -> None:
        """Véletlenszerűen összekeveri a kártyák sorrendjét."""
        random.shuffle(self.cards)

    def get_card(self, index: int) -> Card:
        """Visszaadja az adott indexű kártyát (index = sor * cols + oszlop)."""
        return self.cards[index]

    def pair_count(self) -> int:
        """A pályán lévő párok száma."""
        return len(self.cards) // 2

    def is_finished(self) -> bool:
        """Igaz, ha minden kártya párosítva van."""
        return all(card.is_matched for card in self.cards)
