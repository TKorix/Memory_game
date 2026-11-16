"""scores.py - a ScoreManager osztály: a ranglisták kezelése és mentése JSON fájlba."""
import json
import os
from datetime import datetime
from typing import Callable

import settings as cfg


class ScoreManager:
    """Betölti, rendezi és elmenti az eredményeket kategóriánként.

    Kategória például: "memory_Könnyű" vagy "simon_Normál".
    """

    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.scores: dict[str, list[dict]] = {}
        self.load()

    # ------------------------------------------------------------ fájlkezelés
    def load(self) -> None:
        """Betölti az eredményeket. Ha a fájl nincs meg vagy hibás, üres listával indul."""
        self.scores = {}
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError):
            return  # nincs fájl, vagy sérült: nem baj, üres ranglistával indulunk
        if not isinstance(data, dict):
            return
        for category, entries in data.items():
            if not isinstance(category, str) or not isinstance(entries, list):
                continue
            valid = [e for e in entries if self._is_valid(category, e)]
            self.scores[category] = valid

    def save(self) -> bool:
        """Kiírja az eredményeket a fájlba. Igaz, ha sikerült."""
        temp_name = self.filename + ".tmp"
        try:
            # Előbb egy ideiglenes fájlba írunk, hogy hiba esetén se sérüljön a régi.
            with open(temp_name, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, ensure_ascii=False, indent=2)
            os.replace(temp_name, self.filename)
            return True
        except OSError:
            return False  # pl. csak olvasható mappa: a játék ettől még fut tovább

    @staticmethod
    def _is_valid(category: str, entry: object) -> bool:
        """Ellenőrzi, hogy egy betöltött eredmény használható-e."""
        if not isinstance(entry, dict):
            return False
        if category.startswith("memory_"):
            return isinstance(entry.get("moves"), int) and isinstance(entry.get("seconds"), int)
        if category.startswith("simon_"):
            return isinstance(entry.get("level"), int)
        return False

    # ----------------------------------------------------------- új eredmények
    def add_memory_score(self, difficulty: str, moves: int, seconds: int) -> bool:
        """Kártyapár-kereső eredmény rögzítése (kevesebb lépés, majd kevesebb idő a jobb)."""
        entry = {"moves": moves, "seconds": seconds, "date": self._today()}
        return self._add_score(f"memory_{difficulty}", entry,
                               lambda e: (e["moves"], e["seconds"]))

    def add_simon_score(self, speed: str, level: int) -> bool:
        """Simon eredmény rögzítése (a magasabb szint a jobb). 0 szintet nem mentünk."""
        if level < 1:
            return False
        entry = {"level": level, "date": self._today()}
        return self._add_score(f"simon_{speed}", entry, lambda e: -e["level"])

    def _add_score(self, category: str, entry: dict, sort_key: Callable) -> bool:
        """Közös segédmetódus: beilleszti, rendezi, levágja az 5. utáni részt és ment.

        Igaz, ha az új eredmény lett a legjobb (új rekord).
        """
        results = self.scores.setdefault(category, [])
        results.append(entry)
        results.sort(key=sort_key)      # a rendezés stabil: döntetlennél a régi marad elöl
        del results[cfg.MAX_SCORES:]
        self.save()
        return bool(results) and results[0] is entry

    # ----------------------------------------------------------- lekérdezések
    def get_top(self, category: str) -> list[dict]:
        """Az adott kategória legjobb eredményei (legjobb elöl)."""
        return list(self.scores.get(category, []))[:cfg.MAX_SCORES]

    def get_best(self, category: str) -> dict | None:
        """Az adott kategória legjobb eredménye, vagy None, ha még nincs."""
        top = self.get_top(category)
        return top[0] if top else None

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime("%Y.%m.%d.")
