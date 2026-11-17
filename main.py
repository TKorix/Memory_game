"""main.py - a program belépési pontja.

Indítás:  python main.py
"""
import os
import tkinter as tk

import settings as cfg
from menu import MainMenu
from scores import ScoreManager


def main():
    """Létrehozza az ablakot, a ranglistát és a főmenüt, majd elindítja a programot."""
    root = tk.Tk()
    root.title(cfg.APP_NAME + " – Memóriajátékok")
    root.configure(bg=cfg.BG)
    root.resizable(False, False)

    # Az ablakot a képernyő közepére tesszük
    width = min(cfg.WINDOW_WIDTH, root.winfo_screenwidth() - 40)
    height = min(cfg.WINDOW_HEIGHT, root.winfo_screenheight() - 80)
    x = (root.winfo_screenwidth() - width) // 2
    y = max(0, (root.winfo_screenheight() - height) // 2 - 20)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # A ranglista fájlja a program mellé kerül
    folder = os.path.dirname(os.path.abspath(__file__))
    score_manager = ScoreManager(os.path.join(folder, cfg.SCORE_FILE))

    MainMenu(root, score_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
