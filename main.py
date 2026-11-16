"""main.py - a program belépési pontja.

Indítás:  python main.py
"""
import os
import tkinter as tk

import settings as cfg
from menu import MainMenu
from scores import ScoreManager


def center_window(root: tk.Tk, width: int, height: int) -> None:
    """A képernyő közepére teszi az ablakot."""
    width = min(width, root.winfo_screenwidth() - 40)      # kis képernyőn se lógjon ki
    height = min(height, root.winfo_screenheight() - 80)
    x = (root.winfo_screenwidth() - width) // 2
    y = max(0, (root.winfo_screenheight() - height) // 2 - 20)
    root.geometry(f"{width}x{height}+{x}+{y}")


def main() -> None:
    """Létrehozza az ablakot, a ranglistát és a főmenüt, majd elindítja a programot."""
    root = tk.Tk()
    root.title(f"{cfg.APP_NAME} – Memóriajátékok")
    root.configure(bg=cfg.BG)
    root.resizable(False, False)
    center_window(root, cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT)

    # A ranglista fájlja a program mellé kerül, akárhonnan indítjuk
    folder = os.path.dirname(os.path.abspath(__file__))
    score_manager = ScoreManager(os.path.join(folder, cfg.SCORE_FILE))

    MainMenu(root, score_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
