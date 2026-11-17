"""menu.py - a MainMenu osztály: a főmenü, innen indítjuk a játékokat."""
import random
import tkinter as tk

import settings as cfg
from base_game import format_time, get_rank, styled_button
from memory_game import MemoryGame
from simon_game import SimonGame


class MainMenu:
    """A főmenü: két játék közül lehet választani, és látszanak a rekordok."""

    def __init__(self, root, score_manager):
        self.root = root
        self.score_manager = score_manager
        self.frame = None               # a menü kerete
        self.current_game = None        # az éppen futó játék (None, ha a menü látszik)
        self.show()

    def show(self):
        """Felépíti és megjeleníti a menüt."""
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, bg=cfg.BG)
        self.frame.pack(fill="both", expand=True)

        # Cím: minden betű más színű
        title = tk.Canvas(self.frame, width=460, height=96, bg=cfg.BG, highlightthickness=0)
        title.pack(pady=(34, 0))
        for i, letter in enumerate(cfg.APP_NAME.upper()):
            bright = cfg.SIMON_COLORS[i % 4][1]
            title.create_text(48 + i * 91 + 3, 51, text=letter, fill=cfg.SHADOW,
                              font=(cfg.FONT_FAMILY, 54, "bold"))          # árnyék
            title.create_text(48 + i * 91, 48, text=letter, fill=bright,
                              font=(cfg.FONT_FAMILY, 54, "bold"))
        tk.Label(self.frame, text="Memóriajátékok", bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 16)).pack()

        # A két játék panelje egymás mellett
        panels = tk.Frame(self.frame, bg=cfg.BG)
        panels.pack(pady=30)

        memory_lines = []
        for name in cfg.DIFFICULTIES:
            best = self.score_manager.get_best("memory_" + name)
            result = "–"
            if best:
                result = f"{best['moves']} lépés · {format_time(best['seconds'])}"
            memory_lines.append(f"{name}: {result}")
        self._build_panel(panels, 0, "Kártyapár-kereső",
                          "Fordíts fel két kártyát, és találd meg az összes párt "
                          "minél kevesebb lépésből!", memory_lines, MemoryGame)

        simon_lines = []
        for name in cfg.SIMON_SPEEDS:
            best = self.score_manager.get_best("simon_" + name)
            result = "–"
            if best:
                result = f"{best['level']}. szint · {get_rank(best['level'])}"
            simon_lines.append(f"{name}: {result}")
        self._build_panel(panels, 1, "Színsorozat",
                          "Jegyezd meg a felvillanó színeket, és játszd vissza őket – "
                          "minden kör eggyel hosszabb!", simon_lines, SimonGame)

        styled_button(self.frame, "Kilépés", self.quit).pack()
        tk.Label(self.frame, text=random.choice(cfg.TIPS), bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 10)).pack(pady=(16, 0))

    def _build_panel(self, parent, column, title, description, best_lines, game_class):
        """Egy játék paneljét építi fel: cím, leírás, rekordok, indítógomb."""
        outer = tk.Frame(parent, bg=cfg.PANEL)
        outer.grid(row=0, column=column, padx=14)
        bar = tk.Frame(outer, bg=cfg.PANEL)                 # színes csík a panel tetején
        bar.pack(fill="x")
        for normal, _bright in cfg.SIMON_COLORS:
            tk.Frame(bar, bg=normal, height=5).pack(side="left", expand=True, fill="x")
        panel = tk.Frame(outer, bg=cfg.PANEL, padx=26, pady=20)
        panel.pack()
        tk.Label(panel, text=title, bg=cfg.PANEL, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 18, "bold")).pack()
        tk.Label(panel, text=description, bg=cfg.PANEL, fg=cfg.MUTED, wraplength=270,
                 font=(cfg.FONT_FAMILY, 11)).pack(pady=(10, 14))
        tk.Label(panel, text="Legjobb eredmények", bg=cfg.PANEL, fg=cfg.ACCENT_HI,
                 font=(cfg.FONT_FAMILY, 10, "bold")).pack()
        for line in best_lines:
            tk.Label(panel, text=line, bg=cfg.PANEL, fg=cfg.TEXT,
                     font=(cfg.FONT_FAMILY, 10)).pack()
        styled_button(panel, "Játék indítása", lambda: self.start_game(game_class),
                      primary=True, font_size=12, padx=26, pady=10).pack(pady=(18, 0))

    def start_game(self, game_class):
        """Elrejti a menüt, létrehozza és elindítja a kiválasztott játékot."""
        self.frame.pack_forget()
        self.current_game = game_class(self.root, self.score_manager, self.return_to_menu)
        self.current_game.start()

    def return_to_menu(self):
        """A játék után újra megjeleníti a menüt (friss rekordokkal)."""
        self.current_game = None
        self.show()

    def quit(self):
        """Bezárja a programot."""
        self.root.destroy()
