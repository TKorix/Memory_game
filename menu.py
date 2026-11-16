"""A játék főmenüje."""

import tkinter as tk

import settings as cfg
from base_game import BaseGame
from memory_game import MemoryGame
from scores import ScoreManager
from simon_game import SimonGame


class MainMenu:
    def __init__(self, root: tk.Tk, score_manager: ScoreManager):
        self.root = root
        self.score_manager = score_manager
        self.frame: tk.Frame | None = None
        self.current_game: BaseGame | None = None
        self.show()

    def show(self) -> None:
        if self.frame is not None:
            self.frame.destroy()

        self.frame = tk.Frame(self.root, bg=cfg.BG)
        self.frame.pack(fill="both", expand=True, padx=36, pady=28)

        tk.Label(
            self.frame,
            text="🧠  MEMÓRIA",
            font=(cfg.FONT, 34, "bold"),
            bg=cfg.BG,
            fg=cfg.TEXT,
        ).pack(pady=(26, 4))
        tk.Label(
            self.frame,
            text="Játssz, figyelj, és döntsd meg a saját rekordodat!",
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.MUTED,
        ).pack(pady=(0, 30))

        games = tk.Frame(self.frame, bg=cfg.BG)
        games.pack()
        self.make_game_card(
            games,
            "🃏",
            "Kártyapár-kereső",
            "Találd meg az összes párt minél kevesebb lépésből.",
            "JÁTÉK INDÍTÁSA",
            MemoryGame,
            0,
        )
        self.make_game_card(
            games,
            "🎨",
            "Színsorozat",
            "Jegyezd meg a színeket, és juss egyre tovább!",
            "JÁTÉK INDÍTÁSA",
            SimonGame,
            1,
        )

        tk.Label(
            self.frame,
            text="Minden játék után nézd meg, sikerült-e új rekordot elérned. 🏆",
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.ACCENT,
        ).pack(pady=(26, 12))
        tk.Button(
            self.frame,
            text="Kilépés",
            command=self.quit,
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.MUTED,
            activebackground=cfg.PANEL,
            activeforeground=cfg.TEXT,
            relief="flat",
            padx=16,
            pady=8,
        ).pack()

    def make_game_card(
        self,
        parent: tk.Frame,
        emoji: str,
        title: str,
        description: str,
        button_text: str,
        game_class: type[BaseGame],
        column: int,
    ) -> None:
        card = tk.Frame(parent, bg=cfg.PANEL, padx=24, pady=22, width=370, height=280)
        card.grid(row=0, column=column, padx=12, sticky="nsew")
        card.grid_propagate(False)

        tk.Label(
            card,
            text=emoji,
            font=(cfg.FONT, 34),
            bg=cfg.PANEL,
            fg=cfg.TEXT,
        ).pack(pady=(4, 8))
        tk.Label(
            card,
            text=title,
            font=(cfg.FONT, 18, "bold"),
            bg=cfg.PANEL,
            fg=cfg.TEXT,
        ).pack()
        tk.Label(
            card,
            text=description,
            font=cfg.BODY_FONT,
            bg=cfg.PANEL,
            fg=cfg.MUTED,
            wraplength=290,
            justify="center",
        ).pack(pady=(8, 18))
        tk.Button(
            card,
            text=button_text,
            command=lambda: self.start_game(game_class),
            font=cfg.BUTTON_FONT,
            bg=cfg.ACCENT,
            fg=cfg.BG,
            activebackground=cfg.ACCENT,
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack()

    def start_game(self, game_class: type[BaseGame]) -> None:
        self.frame.pack_forget()
        self.current_game = game_class(
            self.root,
            self.score_manager,
            self.return_to_menu,
        )
        self.current_game.start()

    def return_to_menu(self) -> None:
        self.current_game = None
        self.show()

    def quit(self) -> None:
        self.root.destroy()