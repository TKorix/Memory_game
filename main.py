"""A program indítása: python main.py"""

import tkinter as tk
from pathlib import Path

import settings as cfg
from menu import MainMenu
from scores import ScoreManager


def main():
    root = tk.Tk()
    root.title(f"{cfg.APP_NAME} – Memóriajátékok")
    root.configure(bg=cfg.BG)
    root.geometry(f"{cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}")
    root.resizable(False, False)

    score_file = Path(__file__).with_name(cfg.SCORE_FILE)
    score_manager = ScoreManager(str(score_file))

    MainMenu(root, score_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
