"""board.py - a Board osztály: a játékpálya (a kártyák listája)."""
import random

from card import Card


class Board:
    """A pálya. Létrehozza a kártyapárokat, megkeveri őket."""

    def __init__(self, rows, cols, symbols):
        self.rows = rows
        self.cols = cols
        self.cards = []
        pairs = rows * cols // 2
        # Kiválasztunk annyi szimbólumot, ahány pár kell,
        # és mindegyikből két kártyát csinálunk.
        for symbol in random.sample(symbols, pairs):
            self.cards.append(Card(symbol))
            self.cards.append(Card(symbol))
        self.shuffle()

    def shuffle(self):
        """Összekeveri a kártyákat."""
        random.shuffle(self.cards)

    def get_card(self, index):
        """Visszaadja az adott sorszámú kártyát."""
        return self.cards[index]

    def pair_count(self):
        """Hány pár van a pályán."""
        return len(self.cards) // 2

    def is_finished(self):
        """Igaz, ha minden kártya meg van találva."""
        for card in self.cards:
            if not card.is_matched:
                return False
        return True
