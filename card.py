"""card.py - a Card osztály: egyetlen kártya a kártyapár-kereső játékban."""


class Card:
    """Egy kártya: tudja, melyik szimbólumot rejti, és milyen állapotban van."""

    def __init__(self, value: str) -> None:
        self.value: str = value          # a kártya szimbóluma
        self.is_face_up: bool = False    # fel van-e fordítva
        self.is_matched: bool = False    # megtalálták-e már a párját

    def flip(self) -> None:
        """Megfordítja a kártyát (lefordítottból felfordított lesz, és fordítva)."""
        self.is_face_up = not self.is_face_up

    def hide(self) -> None:
        """Lefordítja a kártyát."""
        self.is_face_up = False

    def set_matched(self) -> None:
        """Párosítottnak jelöli a kártyát, és felfordítva hagyja."""
        self.is_matched = True
        self.is_face_up = True

    def matches(self, other: "Card") -> bool:
        """Igaz, ha a két kártya értéke megegyezik (és nem ugyanaz a kártya)."""
        return self is not other and self.value == other.value

    def __repr__(self) -> str:
        return f"Card({self.value!r}, up={self.is_face_up}, matched={self.is_matched})"
