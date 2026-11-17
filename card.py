"""card.py - a Card osztály: egyetlen kártya."""


class Card:
    """Egy kártya. Tudja, melyik szimbólum van rajta, és hogy fel van-e fordítva."""

    def __init__(self, value):
        self.value = value          # a szimbólum (pl. "★")
        self.is_face_up = False     # fel van-e fordítva?
        self.is_matched = False     # megtalálták-e már a párját?

    def flip(self):
        """Megfordítja a kártyát."""
        self.is_face_up = not self.is_face_up

    def hide(self):
        """Lefordítja a kártyát."""
        self.is_face_up = False

    def set_matched(self):
        """Megtalált párnak jelöli, és felfordítva hagyja."""
        self.is_matched = True
        self.is_face_up = True

    def matches(self, other):
        """Igaz, ha a két kártyán ugyanaz a szimbólum van."""
        return self.value == other.value
