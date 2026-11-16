"""base_game.py - a BaseGame ősosztály és a közös segédfüggvények.

A két játékmód (MemoryGame, SimonGame) ebből az osztályból származik, így
a közös részeket (keret, időzítők, hang, ranglista, visszalépés a menübe)
csak egyszer kellett megírni.
"""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Callable

import settings as cfg

try:
    import winsound  # csak Windowson létezik
except ImportError:
    winsound = None


# ------------------------------------------------------------ segédfüggvények
def format_time(seconds: int) -> str:
    """Másodpercből "pp:mm" formátumú szöveget készít (pl. 75 -> "01:15")."""
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def rounded_rect(canvas: tk.Canvas, x0: float, y0: float, x1: float, y1: float,
                 radius: float, **kwargs) -> int:
    """Lekerekített sarkú téglalapot rajzol a vászonra (poligon + smooth)."""
    radius = max(0, min(radius, (x1 - x0) / 2, (y1 - y0) / 2))
    points = [x0 + radius, y0, x1 - radius, y0, x1, y0, x1, y0 + radius,
              x1, y1 - radius, x1, y1, x1 - radius, y1, x0 + radius, y1,
              x0, y1, x0, y1 - radius, x0, y0 + radius, x0, y0]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def styled_button(parent: tk.Misc, text: str, command: Callable, primary: bool = False,
                  font_size: int = 11, padx: int = 18, pady: int = 8) -> tk.Label:
    """Egyedi kinézetű gomb (egy Label, ami kattintásra a command-ot hívja).

    Label-lel készítjük, mert így minden operációs rendszeren ugyanúgy néz ki.
    """
    label = tk.Label(parent, text=text, fg=cfg.TEXT, cursor="hand2",
                     font=(cfg.FONT_FAMILY, font_size, "bold"), padx=padx, pady=pady)
    set_button_state(label, primary)
    label.bind("<Enter>", lambda event: label.config(bg=label._hover))
    label.bind("<Leave>", lambda event: label.config(bg=label._base))
    label.bind("<Button-1>", lambda event: command())
    return label


def set_button_state(label: tk.Label, active: bool) -> None:
    """Kiemeltre (active=True) vagy normálra állítja a gomb színét."""
    label._base = cfg.ACCENT if active else cfg.PANEL_HI
    label._hover = cfg.ACCENT_HI if active else cfg.BUTTON_HOVER
    label.config(bg=label._base)


# ------------------------------------------------------------------ BaseGame
class BaseGame:
    """A játékmódok közös őse."""

    # Osztályszintű érték: a hang be- vagy kikapcsolása minden játékmódra érvényes.
    sound_enabled: bool = cfg.SOUND_ENABLED

    def __init__(self, root: tk.Tk, score_manager, on_exit: Callable) -> None:
        self.root: tk.Tk = root
        self.score_manager = score_manager
        self.on_exit: Callable = on_exit
        self.frame: tk.Frame = tk.Frame(root, bg=cfg.BG)   # a játék saját kerete
        self._after_ids: list[str] = []      # az éppen várakozó időzítők azonosítói
        self._bound_keys: list[str] = []     # a lefoglalt billentyűk
        self._overlay: tk.Frame | None = None

    # -------------------------------------------------- a leszármazottak dolga
    def start(self) -> None:
        """A leszármazottak felülírják: felépítik a felületet és elindítják a játékot."""
        raise NotImplementedError

    def new_game(self) -> None:
        """A leszármazottak felülírják: új játékot indít."""
        raise NotImplementedError

    def stop(self) -> None:
        """Leállítja az időzítőket és a billentyűkötéseket.

        A leszármazottak kiegészíthetik (super().stop() hívással).
        """
        self._cancel_scheduled()
        for sequence in self._bound_keys:
            self.root.unbind(sequence)
        self._bound_keys = []

    # ------------------------------------------------------------- időzítők
    def _schedule(self, ms: int, func: Callable, *args) -> str:
        """Késleltetve meghívja a func-ot (root.after), és számon tartja az időzítőt."""
        holder: list[str] = []

        def run() -> None:
            if holder and holder[0] in self._after_ids:
                self._after_ids.remove(holder[0])
            func(*args)

        after_id = self.root.after(ms, run)
        holder.append(after_id)
        self._after_ids.append(after_id)
        return after_id

    def _cancel(self, after_id: str | None) -> None:
        """Egyetlen várakozó időzítő megszakítása."""
        if after_id is None:
            return
        try:
            self.root.after_cancel(after_id)
        except tk.TclError:
            pass
        if after_id in self._after_ids:
            self._after_ids.remove(after_id)

    def _cancel_scheduled(self) -> None:
        """Az összes várakozó időzítő megszakítása."""
        for after_id in list(self._after_ids):
            self._cancel(after_id)
        self._after_ids = []

    # ------------------------------------------------------------ billentyűk
    def bind_key(self, sequence: str, func: Callable) -> None:
        """Billentyűparancsot köt a főablakhoz (a stop() majd leveszi)."""
        self.root.bind(sequence, func)
        self._bound_keys.append(sequence)

    # ------------------------------------------------------------------ hang
    def play_melody(self, notes: list[tuple[int, int]]) -> None:
        """Hangsorozatot játszik le külön szálon (hogy a játék ne fagyjon le).

        notes: (frekvencia Hz-ben, hossz ms-ban) párok listája.
        Csak Windowson szól; máshol csendben nem csinál semmit.
        """
        if not BaseGame.sound_enabled or winsound is None:
            return

        def worker() -> None:
            for frequency, duration in notes:
                try:
                    winsound.Beep(max(37, int(frequency)), max(20, int(duration)))
                except Exception:
                    return

        threading.Thread(target=worker, daemon=True).start()

    def play_tone(self, frequency: int, duration: int) -> None:
        """Egyetlen hang lejátszása."""
        self.play_melody([(frequency, duration)])

    def toggle_sound(self) -> bool:
        """Ki-be kapcsolja a hangot; az új állapotot adja vissza."""
        BaseGame.sound_enabled = not BaseGame.sound_enabled
        return BaseGame.sound_enabled

    @staticmethod
    def sound_text() -> str:
        """A hang gomb felirata."""
        return "Hang: be" if BaseGame.sound_enabled else "Hang: ki"

    # -------------------------------------------------------- eredményjelzés
    def show_overlay(self, title: str, lines: list[str], highlight: str = "") -> None:
        """A játék fölé tesz egy eredmény-panelt (Új játék / Főmenü gombokkal)."""
        self.hide_overlay()
        box = tk.Frame(self.frame, bg=cfg.PANEL, highlightbackground=cfg.ACCENT,
                       highlightthickness=2, padx=44, pady=28)
        tk.Label(box, text=title, bg=cfg.PANEL, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 24, "bold")).pack()
        if highlight:
            tk.Label(box, text=highlight, bg=cfg.PANEL, fg=cfg.SUCCESS,
                     font=(cfg.FONT_FAMILY, 14, "bold")).pack(pady=(6, 0))
        for line in lines:
            tk.Label(box, text=line, bg=cfg.PANEL, fg=cfg.MUTED,
                     font=(cfg.FONT_FAMILY, 13)).pack(pady=(6, 0))
        buttons = tk.Frame(box, bg=cfg.PANEL)
        buttons.pack(pady=(20, 0))
        styled_button(buttons, "Új játék", self.new_game, primary=True).pack(side="left", padx=6)
        styled_button(buttons, "Főmenü", self.back_to_menu).pack(side="left", padx=6)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.lift()
        self._overlay = box

    def hide_overlay(self) -> None:
        """Eltünteti az eredmény-panelt, ha éppen látszik."""
        if self._overlay is not None:
            self._overlay.destroy()
            self._overlay = None

    def show_scores(self, category: str) -> None:
        """Felugró ablakban megmutatja az adott kategória top 5 eredményét."""
        mode, _, level = category.partition("_")
        mode_name = {"memory": "Kártyapár-kereső", "simon": "Színsorozat"}.get(mode, mode)
        top = self.score_manager.get_top(category)

        window = tk.Toplevel(self.root)
        window.title("Ranglista")
        window.configure(bg=cfg.BG, padx=34, pady=26)
        window.resizable(False, False)
        window.transient(self.root)

        tk.Label(window, text="Ranglista", bg=cfg.BG, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 20, "bold")).pack()
        tk.Label(window, text=f"{mode_name} – {level}", bg=cfg.BG, fg=cfg.ACCENT_HI,
                 font=(cfg.FONT_FAMILY, 12)).pack(pady=(0, 14))

        if not top:
            tk.Label(window, text="Még nincs eredmény ezen a szinten.", bg=cfg.BG,
                     fg=cfg.MUTED, font=(cfg.FONT_FAMILY, 12)).pack(pady=10)
        for rank, entry in enumerate(top, start=1):
            row = tk.Frame(window, bg=cfg.PANEL)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{rank}.", bg=cfg.PANEL, fg=cfg.ACCENT_HI, width=3,
                     font=(cfg.FONT_FAMILY, 13, "bold")).pack(side="left", padx=(10, 0), pady=8)
            tk.Label(row, text=self._format_score(entry), bg=cfg.PANEL, fg=cfg.TEXT, width=18,
                     anchor="w", font=(cfg.FONT_FAMILY, 13)).pack(side="left", padx=6)
            tk.Label(row, text=entry.get("date", ""), bg=cfg.PANEL, fg=cfg.MUTED,
                     font=(cfg.FONT_FAMILY, 10)).pack(side="right", padx=12)

        styled_button(window, "Bezárás", window.destroy).pack(pady=(18, 0))
        window.bind("<Escape>", lambda event: window.destroy())

        # A főablak közepére igazítjuk
        window.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - window.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - window.winfo_height()) // 2
        window.geometry(f"+{max(0, x)}+{max(0, y)}")
        window.focus_set()

    @staticmethod
    def _format_score(entry: dict) -> str:
        """Egy eredményt olvasható szöveggé alakít."""
        if "level" in entry:
            return f"{entry['level']}. szint"
        return f"{entry['moves']} lépés · {format_time(entry['seconds'])}"

    # ------------------------------------------------------------ visszalépés
    def back_to_menu(self) -> None:
        """Leállítja a játékot, bezárja a keretét, és visszatér a főmenübe."""
        self.stop()
        self.hide_overlay()
        self.frame.destroy()
        self.on_exit()
