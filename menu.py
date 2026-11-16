"""menu.py - a MainMenu osztály: a főmenü és a játékmódok indítása."""
import tkinter as tk

import settings as cfg
from base_game import BaseGame, format_time, rounded_rect, styled_button
from memory_game import MemoryGame
from simon_game import SimonGame


class MainMenu:
    """A főmenü: két játékmód közül lehet választani, és látszanak a rekordok."""

    def __init__(self, root: tk.Tk, score_manager) -> None:
        self.root: tk.Tk = root
        self.score_manager = score_manager
        self.frame: tk.Frame | None = None
        self.current_game: BaseGame | None = None    # az éppen futó játékmód
        self.show()

    def show(self) -> None:
        """Felépíti és megjeleníti a menüt."""
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, bg=cfg.BG)
        self.frame.pack(fill="both", expand=True)

        # Cím
        tk.Label(self.frame, text=cfg.APP_NAME.upper(), bg=cfg.BG, fg=cfg.ACCENT_HI,
                 font=(cfg.FONT_FAMILY, 52, "bold")).pack(pady=(30, 0))
        tk.Label(self.frame, text="Memóriajátékok", bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 16)).pack()

        # Dísz: a Simon négy színe
        deco = tk.Canvas(self.frame, width=200, height=44, bg=cfg.BG, highlightthickness=0)
        deco.pack(pady=(14, 0))
        for i, (normal, _bright) in enumerate(cfg.SIMON_COLORS):
            rounded_rect(deco, 6 + i * 48, 6, 42 + i * 48, 38, 10, fill=normal, outline="")

        # A két játékmód panelje
        panels = tk.Frame(self.frame, bg=cfg.BG)
        panels.pack(pady=24)

        memory_lines = []
        for name in cfg.DIFFICULTIES:
            best = self.score_manager.get_best(f"memory_{name}")
            result = f"{best['moves']} lépés · {format_time(best['seconds'])}" if best else "–"
            memory_lines.append(f"{name}: {result}")
        self._build_panel(
            panels, 0, "Kártyapár-kereső",
            "Fordíts fel két kártyát, és találd meg az összes párt minél kevesebb lépésből!",
            memory_lines, MemoryGame)

        simon_lines = []
        for name in cfg.SIMON_SPEEDS:
            best = self.score_manager.get_best(f"simon_{name}")
            simon_lines.append(f"{name}: {str(best['level']) + '. szint' if best else '–'}")
        self._build_panel(
            panels, 1, "Színsorozat",
            "Jegyezd meg a felvillanó színeket, és játszd vissza őket – minden kör eggyel hosszabb!",
            simon_lines, SimonGame)

        styled_button(self.frame, "Kilépés", self.quit).pack()

    def _build_panel(self, parent: tk.Frame, column: int, title: str, description: str,
                     best_lines: list[str], game_class: type) -> None:
        """Egy játékmód paneljét készíti el: cím, leírás, rekordok és indítógomb."""
        panel = tk.Frame(parent, bg=cfg.PANEL, padx=26, pady=22)
        panel.grid(row=0, column=column, padx=14)
        tk.Label(panel, text=title, bg=cfg.PANEL, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 18, "bold")).pack()
        tk.Label(panel, text=description, bg=cfg.PANEL, fg=cfg.MUTED, wraplength=270,
                 justify="center", font=(cfg.FONT_FAMILY, 11)).pack(pady=(10, 14))
        tk.Label(panel, text="Legjobb eredmények", bg=cfg.PANEL, fg=cfg.ACCENT_HI,
                 font=(cfg.FONT_FAMILY, 10, "bold")).pack()
        for line in best_lines:
            tk.Label(panel, text=line, bg=cfg.PANEL, fg=cfg.TEXT,
                     font=(cfg.FONT_FAMILY, 10)).pack()
        styled_button(panel, "Játék indítása", lambda: self.start_game(game_class),
                      primary=True, font_size=12, padx=26, pady=10).pack(pady=(18, 0))

    def start_game(self, game_class: type) -> None:
        """Elrejti a menüt, létrehozza és elindítja a kiválasztott játékmódot."""
        self.frame.pack_forget()
        self.current_game = game_class(self.root, self.score_manager, self.return_to_menu)
        self.current_game.start()

    def return_to_menu(self) -> None:
        """A játék bezárása után újra megjeleníti a menüt (friss rekordokkal)."""
        self.current_game = None
        self.show()

    def quit(self) -> None:
        """Bezárja a programot."""
        self.root.destroy()
