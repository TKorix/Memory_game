"""A Simon-féle színsorozat-játék."""

import random
import tkinter as tk
from tkinter import messagebox
from collections.abc import Callable

import settings as cfg
from base_game import BaseGame
from scores import ScoreManager


class SimonGame(BaseGame):
    def __init__(
        self,
        root: tk.Tk,
        score_manager: ScoreManager,
        on_exit: Callable[[], None],
    ):
        super().__init__(root, score_manager, on_exit)
        self.speed = "Normál"
        self.sequence: list[int] = []
        self.player_pos = 0
        self.level = 0
        self.accepting_input = False
        self.buttons: list[tk.Button] = []
        self.level_label: tk.Label | None = None
        self.status_label: tk.Label | None = None
        self.speed_var = tk.StringVar(value=self.speed)
        self.after_ids: list[str] = []

    def start(self) -> None:
        self.build_ui()
        self.new_game()

    def build_ui(self) -> None:
        self.frame.pack(fill="both", expand=True, padx=30, pady=20)

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
            text="Színsorozat",
            font=cfg.TITLE_FONT,
            bg=cfg.BG,
            fg=cfg.TEXT,
        ).pack(side="left", padx=20)

        self.level_label = tk.Label(
            self.frame,
            text="0. szint",
            font=(cfg.FONT, 22, "bold"),
            bg=cfg.BG,
            fg=cfg.ACCENT,
        )
        self.level_label.pack(pady=(36, 4))

        self.status_label = tk.Label(
            self.frame,
            text="Jegyezd meg a színeket!",
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.MUTED,
        )
        self.status_label.pack(pady=(0, 18))

        grid = tk.Frame(self.frame, bg=cfg.BG)
        grid.pack()
        for index in range(4):
            button = tk.Button(
                grid,
                text="",
                command=lambda color_index=index: self.on_color_click(color_index),
                bg=cfg.SIMON_COLORS[index],
                activebackground=cfg.SIMON_LIGHT_COLORS[index],
                relief="flat",
                width=12,
                height=5,
                cursor="hand2",
            )
            button.grid(row=index // 2, column=index % 2, padx=10, pady=10)
            self.buttons.append(button)

        controls = tk.Frame(self.frame, bg=cfg.BG)
        controls.pack(pady=24)
        tk.Label(
            controls,
            text="Sebesség",
            font=cfg.BODY_FONT,
            bg=cfg.BG,
            fg=cfg.MUTED,
        ).pack(side="left", padx=8)
        tk.OptionMenu(
            controls,
            self.speed_var,
            *cfg.SIMON_SPEEDS.keys(),
            command=self.change_speed,
        ).pack(side="left", padx=8)

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
        ).pack(side="left", padx=8)
        tk.Button(
            controls,
            text="🏆 Ranglista",
            command=lambda: self.show_scores(f"simon_{self.speed}"),
            font=cfg.BODY_FONT,
            bg=cfg.BUTTON,
            fg=cfg.TEXT,
            activebackground=cfg.BUTTON_HOVER,
            activeforeground=cfg.TEXT,
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left", padx=8)

    def change_speed(self, speed: str) -> None:
        self.speed = speed

    def new_game(self) -> None:
        self.stop()
        self.speed = self.speed_var.get()
        self.sequence = []
        self.player_pos = 0
        self.level = 0

        for index, button in enumerate(self.buttons):
            button.config(bg=cfg.SIMON_COLORS[index])

        self.level_label.config(text="0. szint")
        self.status_label.config(text="Figyeld a színeket, aztán ismételd meg őket!")
        self.next_round()

    def next_round(self) -> None:
        self.sequence.append(random.randrange(4))
        self.level = len(self.sequence)
        self.player_pos = 0
        self.level_label.config(text=f"{self.level}. szint")
        self.play_sequence()

    def play_sequence(self) -> None:
        self.accepting_input = False
        self.status_label.config(text="Figyelj! 👀", fg=cfg.ACCENT)

        delay = cfg.SIMON_SPEEDS[self.speed]
        for position, color_index in enumerate(self.sequence):
            self.schedule(delay * (position + 1), self.flash, color_index)

        self.schedule(delay * len(self.sequence) + 100, self.start_turn)

    def start_turn(self) -> None:
        self.accepting_input = True
        self.status_label.config(text="Te jössz! Ismételd meg a sorozatot.", fg=cfg.TEXT)

    def flash(self, index: int) -> None:
        self.buttons[index].config(bg=cfg.SIMON_LIGHT_COLORS[index])
        self.schedule(
            cfg.SIMON_FLASH_DELAY,
            self.reset_button_color,
            index,
        )

    def reset_button_color(self, index: int) -> None:
        self.buttons[index].config(bg=cfg.SIMON_COLORS[index])

    def on_color_click(self, index: int) -> None:
        if not self.accepting_input:
            return

        self.flash(index)
        self.check_input(index)

    def check_input(self, index: int) -> None:
        if index != self.sequence[self.player_pos]:
            self.game_over()
            return

        self.player_pos += 1
        if self.player_pos == len(self.sequence):
            self.accepting_input = False
            self.status_label.config(text="Helyes! Jön a következő szint! ✨", fg=cfg.GOOD)
            self.schedule(700, self.next_round)

    def game_over(self) -> None:
        self.accepting_input = False
        is_record = self.score_manager.add_simon_score(self.speed, self.level)
        self.status_label.config(text=f"Vége! {self.level} szintig jutottál.", fg=cfg.BAD)

        best = self.score_manager.get_best(f"simon_{self.speed}")
        message = f"Most {self.level} szintig jutottál."
        if best is not None:
            message += f"\nA legjobb eredményed: {best['level']} szint."
        if is_record:
            message += "\n\n🏆 Új rekord!"
        message += "\n\nNyomd meg az „Új játék” gombot egy új próbához!"
        messagebox.showinfo("Játék vége", message, parent=self.root)

    def schedule(self, delay: int, function: Callable, *args: object) -> None:
        job_id: str | None = None

        def run() -> None:
            if job_id in self.after_ids:
                self.after_ids.remove(job_id)
            function(*args)

        job_id = self.root.after(delay, run)
        self.after_ids.append(job_id)

    def stop(self) -> None:
        self.accepting_input = False
        for job_id in self.after_ids:
            self.root.after_cancel(job_id)
        self.after_ids = []