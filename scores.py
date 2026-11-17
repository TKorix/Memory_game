"""scores.py - a ScoreManager osztály: a ranglista mentése és betöltése (JSON fájl)."""
import json
from datetime import datetime

import settings as cfg


class ScoreManager:
    """A legjobb eredményeket tárolja kategóriánként.

    A kategória neve pl.: "memory_Könnyű" vagy "simon_Normál".
    """

    def __init__(self, filename):
        self.filename = filename
        self.scores = {}        # kategória -> eredmények listája
        self.load()

    def load(self):
        """Betölti a fájlt. Ha nincs meg vagy hibás, üres ranglistával indulunk."""
        self.scores = {}
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            for category, results in data.items():
                if isinstance(results, list):
                    self.scores[category] = [r for r in results if isinstance(r, dict)]

    def save(self):
        """Kiírja a ranglistát a fájlba."""
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, ensure_ascii=False, indent=2)
        except OSError:
            pass    # ha nem sikerül menteni, a játék ettől még fut tovább

    def add_memory_score(self, difficulty, moves, seconds):
        """Kártyapár-kereső eredmény: kevesebb lépés a jobb, döntetlennél a kevesebb idő."""
        entry = {"moves": moves, "seconds": seconds, "date": self._today()}
        return self._add_score("memory_" + difficulty, entry,
                               lambda e: (e.get("moves", 9999), e.get("seconds", 9999)))

    def add_simon_score(self, speed, level):
        """Simon eredmény: a magasabb szint a jobb. A 0 szintet nem mentjük."""
        if level < 1:
            return False
        entry = {"level": level, "date": self._today()}
        return self._add_score("simon_" + speed, entry, lambda e: -e.get("level", 0))

    def _add_score(self, category, entry, sort_key):
        """Beteszi az eredményt, sorba rendezi, csak az első 5-öt tartja meg, és ment.

        Igaz, ha az új eredmény lett az első (új rekord).
        """
        results = self.scores.setdefault(category, [])
        results.append(entry)
        results.sort(key=sort_key)
        del results[cfg.MAX_SCORES:]
        self.save()
        return results[0] is entry

    def get_top(self, category):
        """Az adott kategória legjobb eredményei."""
        return self.scores.get(category, [])

    def get_best(self, category):
        """Az adott kategória legjobb eredménye, vagy None, ha még nincs."""
        top = self.get_top(category)
        if top:
            return top[0]
        return None

    def _today(self):
        return datetime.now().strftime("%Y.%m.%d.")
