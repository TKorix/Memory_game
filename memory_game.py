"""A kártyapár-kereső játékmód."""

import tkinter as tk
from tkinter import messagebox
from collections.abc import Callable

import settings as cfg
from base_game import BaseGame
from board import Board
from scores import ScoreManager


class MemoryGame(BaseGame):
    def __init__(
        self,
        root: tk.Tk,
        score_manager: ScoreManager,
        on_exit: Callable[[], None],
    ):
        super().__init__(root, score_manager, on_exit)
        self.difficulty = "Könnyű"
        self.board = Board(3, 4, cfg.SYMBOLS)
        self.buttons: list[tk.Button] = []
        self.first_index: int | None = None
        self.locked = False
        self.moves = 0
        self.seconds = 0
        self.timer_running = False
        self.timer_id: str | None = None
        self.mismatch_id: str | None = None
        self.moves_label: tk.Label | None = None
        self.time_label: tk.Label | None = None
        self.status_label: tk.Label | None = None
        self.difficulty_var = tk.StringVar(value=self.difficulty)

    def start(self) -> None:
        self.build_ui()
        self.new_game()

    def build_ui(self) -> None:
        self.frame.pack(fill="both", expand=True, padx=24, pady=18)

        header = tk.Frame(self.frame, bg=cfg.BG)
        header.pack(fill="x")
        tk.Button(
            header,
            text="←  Menü",
            command=self.back_to_menu,
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.MUTED,
            activebackground=cfg.PANEL,
            activeforeground=cfg.TEXT,
            relief="flat",
        ).pack(side="left")
        tk.Label(
            header,
            text="Kártyapár-kereső",
            font=cfg.TITLE_FONT,
            bg=cfg.BG,
            fg=cfg.TEXT,
        ).pack(side="left", padx=20)

        controls = tk.Frame(self.frame, bg=cfg.BG)
        controls.pack(fill="x", pady=(14, 12))

        tk.Label(
            controls,
            text="Nehézség",
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.MUTED,
        ).pack(side="left", padx=(0, 8))
        tk.OptionMenu(
            controls,
            self.difficulty_var,
            *cfg.DIFFICULTIES.keys(),
            command=self.change_difficulty,
        ).pack(side="left")

        self.moves_label = self.make_stat(controls, "Lépések", "0")
        self.time_label = self.make_stat(controls, "Idő", "0 mp")

        tk.Button(
            controls,
            text="Új játék",
            command=self.new_game,
            font=cfg.BUTTON_FONT,
            bg=cfg.ACCENT,
            fg=cfg.BG,
            activebackground=cfg.ACCENT,
            relief="flat",
            padx=16,
            pady=8,
        ).pack(side="right", padx=(8, 0))
        tk.Button(
            controls,
            text="🏆 Ranglista",
            command=lambda: self.show_scores(f"memory_{self.difficulty}"),
            font=cfg.BODY_FONT,
            bg=cfg.BUTTON,
            fg=cfg.TEXT,
            activebackground=cfg.BUTTON_HOVER,
            activeforeground=cfg.TEXT,
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="right")

        self.status_label = tk.Label(
            self.frame,
            text="Találd meg az összes párt!",
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.ACCENT,
        )
        self.status_label.pack(pady=(0, 12))

        self.board_frame = tk.Frame(self.frame, bg=cfg.BG)
        self.board_frame.pack(expand=True)

    def make_stat(self, parent: tk.Frame, title: str, value: str) -> tk.Label:
        box = tk.Frame(parent, bg=cfg.PANEL, padx=12, pady=6)
        box.pack(side="left", padx=6)
        tk.Label(
            box,
            text=title,
            font=(cfg.FONT, 9),
            bg=cfg.PANEL,
            fg=cfg.MUTED,
        ).pack()
        label = tk.Label(
            box,
            text=value,
            font=(cfg.FONT, 13, "bold"),
            bg=cfg.PANEL,
            fg=cfg.TEXT,
        )
        label.pack()
        return label

    def change_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.new_game()

    def new_game(self) -> None:
        self.stop()
        self.difficulty = self.difficulty_var.get()
        rows, cols = cfg.DIFFICULTIES[self.difficulty]
        self.board = Board(rows, cols, cfg.SYMBOLS)
        self.first_index = None
        self.locked = False
        self.moves = 0
        self.seconds = 0

        for button in self.buttons:
            button.destroy()
        self.buttons = []

        self.draw_board()
        self.update_labels()
        self.status_label.config(text="Találd meg az összes párt!", fg=cfg.ACCENT)

    def draw_board(self) -> None:
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                index = row * self.board.cols + col
                button = tk.Button(
                    self.board_frame,
                    text="?",
                    command=lambda card_index=index: self.on_card_click(card_index),
                    font=cfg.CARD_FONT,
                    bg=cfg.CARD_BACK,
                    fg=cfg.TEXT,
                    activebackground=cfg.BUTTON_HOVER,
                    activeforeground=cfg.TEXT,
                    relief="flat",
                    width=5,
                    height=2,
                    cursor="hand2",
                )
                button.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
                self.buttons.append(button)

    def update_card_button(self, index: int) -> None:
        card = self.board.get_card(index)
        button = self.buttons[index]

        if card.is_matched:
            button.config(
                text=card.value,
                bg=cfg.GOOD,
                fg=cfg.BG,
                disabledforeground=cfg.BG,
                state="disabled",
            )
        elif card.is_face_up:
            button.config(text=card.value, bg=cfg.CARD_FRONT, fg=cfg.BG)
        else:
            button.config(text="?", bg=cfg.CARD_BACK, fg=cfg.TEXT, state="normal")

    def on_card_click(self, index: int) -> None:
        if self.locked:
            return

        card = self.board.get_card(index)
        if card.is_matched or card.is_face_up:
            return

        card.flip()
        self.update_card_button(index)

        if not self.timer_running:
            self.timer_running = True
            self.timer_id = self.root.after(1000, self.tick)

        if self.first_index is None:
            self.first_index = index
            return

        self.moves += 1
        self.update_labels()
        self.check_pair(self.first_index, index)

    def check_pair(self, first: int, second: int) -> None:
        first_card = self.board.get_card(first)
        second_card = self.board.get_card(second)

        if first_card.matches(second_card):
            first_card.set_matched()
            second_card.set_matched()
            self.update_card_button(first)
            self.update_card_button(second)
            self.status_label.config(text="Szép! Megvan egy pár! ✨", fg=cfg.GOOD)
            self.first_index = None

            if self.board.is_finished():
                self.finish_game()
        else:
            self.locked = True
            self.status_label.config(text="Nem egyeznek — próbáld újra!", fg=cfg.MUTED)
            self.mismatch_id = self.root.after(
                cfg.MISMATCH_DELAY,
                lambda: self.hide_mismatch(first, second),
            )

    def hide_mismatch(self, first: int, second: int) -> None:
        self.board.get_card(first).hide()
        self.board.get_card(second).hide()
        self.update_card_button(first)
        self.update_card_button(second)
        self.first_index = None
        self.locked = False
        self.mismatch_id = None
        self.status_label.config(text="Jöhet a következő pár!", fg=cfg.ACCENT)

    def tick(self) -> None:
        if not self.timer_running:
            return

        self.seconds += 1
        self.update_labels()
        self.timer_id = self.root.after(1000, self.tick)

    def update_labels(self) -> None:
        self.moves_label.config(text=str(self.moves))
        self.time_label.config(text=f"{self.seconds} mp")

    def finish_game(self) -> None:
        self.timer_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        is_record = self.score_manager.add_memory_score(
            self.difficulty,
            self.moves,
            self.seconds,
        )
        self.status_label.config(text="Minden pár megvan! 🎉", fg=cfg.GOOD)
        message = (
            f"Ügyes vagy! {self.moves} lépésből, {self.seconds} másodperc alatt "
            "megtaláltad az összes párt."
        )
        if is_record:
            message += "\n\n🏆 Új rekord!"
        messagebox.showinfo("Játék vége", message, parent=self.root)

    def stop(self) -> None:
        self.timer_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.mismatch_id is not None:
            self.root.after_cancel(self.mismatch_id)
            self.mismatch_id = None