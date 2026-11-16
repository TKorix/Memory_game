"""A két játékmód közös alapja."""

import tkinter as tk
from collections.abc import Callable

import settings as cfg
from scores import ScoreManager


class BaseGame:
    def __init__(
        self,
        root: tk.Tk,
        score_manager: ScoreManager,
        on_exit: Callable[[], None],
    ):
        self.root = root
        self.score_manager = score_manager
        self.on_exit = on_exit
        self.frame = tk.Frame(root, bg=cfg.BG)

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        pass

    def show_scores(self, category: str) -> None:
        window = tk.Toplevel(self.root)
        window.title("Ranglista")
        window.configure(bg=cfg.BG)
        window.resizable(False, False)
        window.transient(self.root)

        tk.Label(
            window,
            text="🏆  Ranglista",
            font=cfg.TITLE_FONT,
            bg=cfg.BG,
            fg=cfg.TEXT,
        ).pack(padx=28, pady=(22, 8))

        entries = self.score_manager.get_top(category)
        if not entries:
            tk.Label(
                window,
                text="Még nincs eredmény. Te lehetsz az első!",
                font=cfg.BODY_FONT,
                bg=cfg.BG,
                fg=cfg.MUTED,
            ).pack(padx=28, pady=14)
        else:
            for place, entry in enumerate(entries, start=1):
                if "moves" in entry:
                    result = f'{entry["moves"]} lépés · {entry["seconds"]} mp'
                else:
                    result = f'{entry["level"]}. szint'

                tk.Label(
                    window,
                    text=f"{place}.   {result}",
                    font=cfg.BODY_FONT,
                    bg=cfg.PANEL,
                    fg=cfg.TEXT,
                    padx=18,
                    pady=8,
                    width=28,
                    anchor="w",
                ).pack(padx=20, pady=3)

        tk.Button(
            window,
            text="Bezárás",
            command=window.destroy,
            font=cfg.BUTTON_FONT,
            bg=cfg.BUTTON,
            fg=cfg.TEXT,
            activebackground=cfg.BUTTON_HOVER,
            activeforeground=cfg.TEXT,
            relief="flat",
            padx=20,
            pady=8,
        ).pack(pady=(14, 22))

    def back_to_menu(self) -> None:
        self.stop()
        self.frame.destroy()
        self.on_exit()