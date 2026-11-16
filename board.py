"""A memóriajáték kártyáit és pályáját kezeli."""

import random

from card import Card


class Board:
    def __init__(self, rows: int, cols: int, symbols: list[str]):
        self.rows = rows
        self.cols = cols
        number_of_pairs = rows * cols // 2

        if len(symbols) < number_of_pairs:
            raise ValueError("Nincs elég szimbólum ehhez a pályához.")

        self.cards = []
        for symbol in symbols[:number_of_pairs]:
            self.cards.append(Card(symbol))
            self.cards.append(Card(symbol))

        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def get_card(self, index: int) -> Card:
        return self.cards[index]

    def pair_count(self) -> int:
        return len(self.cards) // 2

    def is_finished(self) -> bool:
        for card in self.cards:
            if not card.is_matched:
                return False
        return True