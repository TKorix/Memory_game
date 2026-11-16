"""Egyetlen memóriajáték-kártya."""


class Card:
    def __init__(self, value: str):
        self.value = value
        self.is_face_up = False
        self.is_matched = False

    def flip(self) -> None:
        self.is_face_up = True

    def hide(self) -> None:
        self.is_face_up = False

    def set_matched(self) -> None:
        self.is_matched = True
        self.is_face_up = True

    def matches(self, other: "Card") -> bool:
        return self.value == other.value