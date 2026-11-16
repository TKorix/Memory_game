"""A két játék legjobb eredményeit menti el."""

import json
from collections.abc import Callable


class ScoreManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.scores: dict[str, list[dict]] = {}
        self.load()

    def load(self) -> None:
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                saved_scores = json.load(file)
        except FileNotFoundError:
            self.scores = {}
            return
        except json.JSONDecodeError:
            self.scores = {}
            return

        if isinstance(saved_scores, dict):
            self.scores = {
                category: entries
                for category, entries in saved_scores.items()
                if isinstance(category, str)
                and isinstance(entries, list)
                and all(isinstance(entry, dict) for entry in entries)
            }
        else:
            self.scores = {}

    def save(self) -> None:
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.scores, file, ensure_ascii=False, indent=2)

    def add_memory_score(self, difficulty: str, moves: int, seconds: int) -> bool:
        category = f"memory_{difficulty}"
        entry = {"moves": moves, "seconds": seconds}
        return self._add_score(
            category,
            entry,
            lambda score: (score["moves"], score["seconds"]),
        )

    def add_simon_score(self, speed: str, level: int) -> bool:
        category = f"simon_{speed}"
        entry = {"level": level}
        return self._add_score(category, entry, lambda score: -score["level"])

    def _add_score(
        self,
        category: str,
        entry: dict,
        sort_key: Callable[[dict], int | tuple[int, int]],
    ) -> bool:
        old_scores = self.get_top(category)
        is_record = not old_scores or sort_key(entry) < sort_key(old_scores[0])

        new_scores = old_scores + [entry]
        new_scores.sort(key=sort_key)
        self.scores[category] = new_scores[:5]
        self.save()
        return is_record

    def get_top(self, category: str) -> list[dict]:
        return self.scores.get(category, [])

    def get_best(self, category: str) -> dict | None:
        top_scores = self.get_top(category)
        if top_scores:
            return top_scores[0]
        return None