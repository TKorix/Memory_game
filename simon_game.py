"""simon_game.py - a SimonGame osztály: a színsorozat-játékmód."""
from __future__ import annotations

import random
import tkinter as tk
from typing import Callable

import settings as cfg
from base_game import BaseGame, rounded_rect, set_button_state, styled_button


class SimonGame(BaseGame):
    """Simon: a program felvillant egy színsorozatot, a játékosnak vissza kell játszania.

    Minden helyes kör után a sorozat eggyel hosszabb lesz. Az első hibáig tart.
    """

    def __init__(self, root: tk.Tk, score_manager, on_exit: Callable) -> None:
        super().__init__(root, score_manager, on_exit)
        self.speed: str = "Normál"                  # a kiválasztott sebesség
        self.sequence: list[int] = []               # a megjegyzendő színek (0-3)
        self.player_pos: int = 0                    # hányadiknál tart a játékos
        self.level: int = 0                         # az aktuális kör (= a sorozat hossza)
        self.accepting_input: bool = False          # nyomhat-e most a játékos
        self.buttons: list[tk.Canvas] = []          # a négy színes gomb (vászon)
        self.level_label: tk.Label | None = None
        self.status_label: tk.Label | None = None
        # belső segédek
        self._speed_buttons: dict[str, tk.Label] = {}
        self._best_label: tk.Label | None = None
        self._sound_button: tk.Label | None = None

    # ----------------------------------------------------------- indítás
    def start(self) -> None:
        """Megjeleníti a játék keretét, felépíti a felületet és elindítja az első játékot."""
        self.frame.pack(fill="both", expand=True)
        self.bind_key("<Escape>", lambda event: self.back_to_menu())
        self.bind_key("<space>", lambda event: self.new_game())
        self.bind_key("<Key-m>", lambda event: self._on_sound_toggle())
        for index in range(4):                       # 1-4 billentyűk a színekhez
            self.bind_key(f"<Key-{index + 1}>", lambda event, i=index: self.on_color_click(i))
        self.build_ui()
        self.new_game()

    def build_ui(self) -> None:
        """Létrehozza a négy színes gombot, a sebességválasztót, a feliratokat és a gombokat."""
        header = tk.Frame(self.frame, bg=cfg.BG)
        header.pack(fill="x", padx=30, pady=(22, 4))
        tk.Label(header, text="Színsorozat", bg=cfg.BG, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 24, "bold")).pack(side="left")
        self._best_label = tk.Label(header, text="", bg=cfg.BG, fg=cfg.MUTED,
                                    font=(cfg.FONT_FAMILY, 11))
        self._best_label.pack(side="right")

        self.level_label = tk.Label(self.frame, bg=cfg.PANEL, fg=cfg.TEXT, width=16, pady=8,
                                    font=(cfg.FONT_FAMILY, 14, "bold"))
        self.level_label.pack(pady=(10, 4))
        self.status_label = tk.Label(self.frame, text="", bg=cfg.BG, fg=cfg.ACCENT_HI,
                                     font=(cfg.FONT_FAMILY, 18, "bold"))
        self.status_label.pack(pady=(4, 0))

        # Sebességválasztó
        speeds = tk.Frame(self.frame, bg=cfg.BG)
        speeds.pack(pady=(6, 0))
        tk.Label(speeds, text="Sebesség:", bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 11)).pack(side="left", padx=(0, 8))
        for name in cfg.SIMON_SPEEDS:
            button = styled_button(speeds, name, lambda n=name: self._set_speed(n),
                                   font_size=10, padx=14, pady=5)
            button.pack(side="left", padx=4)
            self._speed_buttons[name] = button

        # A négy színes gomb 2x2-es rácsban
        pad = tk.Frame(self.frame, bg=cfg.BG)
        pad.pack(expand=True)
        self.buttons = []
        for index in range(4):
            canvas = tk.Canvas(pad, width=cfg.SIMON_SIZE, height=cfg.SIMON_SIZE, bg=cfg.BG,
                               highlightthickness=0, cursor="hand2")
            row, col = divmod(index, 2)
            canvas.grid(row=row, column=col, padx=8, pady=8)
            canvas.bind("<Button-1>", lambda event, i=index: self.on_color_click(i))
            self.buttons.append(canvas)
            self._draw_button(index, lit=False)

        # Alsó gombsor
        bottom = tk.Frame(self.frame, bg=cfg.BG)
        bottom.pack(pady=(0, 6))
        styled_button(bottom, "Új játék", self.new_game, primary=True).pack(side="left", padx=5)
        styled_button(bottom, "Ranglista",
                      lambda: self.show_scores(self._category())).pack(side="left", padx=5)
        self._sound_button = styled_button(bottom, self.sound_text(), self._on_sound_toggle)
        self._sound_button.pack(side="left", padx=5)
        styled_button(bottom, "Vissza a menübe", self.back_to_menu).pack(side="left", padx=5)
        tk.Label(self.frame, text="Esc: menü  ·  Szóköz: új játék  ·  1-4: színek  ·  M: hang",
                 bg=cfg.BG, fg=cfg.MUTED, font=(cfg.FONT_FAMILY, 9)).pack(pady=(0, 12))

    # --------------------------------------------------------- új játék
    def new_game(self) -> None:
        """Kiüríti a sorozatot, nullázza a szintet, és elindítja az első kört."""
        self._cancel_scheduled()
        self.hide_overlay()
        self.sequence = []
        self.player_pos = 0
        self.level = 0
        self.accepting_input = False
        for name, button in self._speed_buttons.items():
            set_button_state(button, name == self.speed)
        for index in range(4):
            self._draw_button(index, lit=False)
        self.level_label.config(text="Szint: 0")
        self.status_label.config(text="Készülj!", fg=cfg.ACCENT_HI)
        self._update_best_label()
        self._schedule(cfg.SIMON_START_DELAY, self.next_round)

    def next_round(self) -> None:
        """Új véletlen színt fűz a sorozat végére, és lejátssza az egészet."""
        self.sequence.append(random.randrange(4))
        self.level += 1
        self.player_pos = 0
        self.level_label.config(text=f"Szint: {self.level}")
        self.play_sequence()

    def play_sequence(self) -> None:
        """Egymás után felvillantja a sorozat elemeit, a végén engedélyezi a bevitelt."""
        self.accepting_input = False
        self.status_label.config(text="Figyelj!", fg=cfg.ACCENT_HI)
        flash_ms, gap_ms = self._timing()
        wait = 300
        for color_index in self.sequence:
            self._schedule(wait, self.flash, color_index, flash_ms)
            wait += flash_ms + gap_ms
        self._schedule(wait, self._enable_input)

    def _enable_input(self) -> None:
        """A sorozat lejátszása után a játékos jön."""
        self.accepting_input = True
        self.status_label.config(text="Te jössz!", fg=cfg.SUCCESS)

    def _timing(self) -> tuple[int, int]:
        """A lejátszás sebessége: a választott szinttől függ, és minden körben gyorsul."""
        flash_ms, gap_ms = cfg.SIMON_SPEEDS[self.speed]
        faster = (self.level - 1) * cfg.SIMON_SPEEDUP
        return (max(cfg.SIMON_MIN_FLASH, flash_ms - faster),
                max(cfg.SIMON_MIN_GAP, gap_ms - faster // 2))

    # ------------------------------------------------------------ megjelenés
    def _draw_button(self, index: int, lit: bool) -> None:
        """Lerajzolja a színes gombot; lit=True esetén felvillanva."""
        canvas = self.buttons[index]
        normal, bright = cfg.SIMON_COLORS[index]
        size = cfg.SIMON_SIZE
        canvas.delete("all")
        rounded_rect(canvas, 12, 14, size - 6, size - 4, 40, fill=cfg.SHADOW, outline="")
        if lit:
            rounded_rect(canvas, 6, 6, size - 10, size - 10, 40, fill=bright,
                         outline="#ffffff", width=4)
        else:
            rounded_rect(canvas, 6, 6, size - 10, size - 10, 40, fill=normal, outline="")
            # finom fényes sáv a gomb tetején
            rounded_rect(canvas, 22, 16, size - 26, 40, 12,
                         fill=self._mix(normal, bright, 0.25), outline="")
        canvas.create_text(size - 34, size - 32, text=str(index + 1), fill=cfg.TEXT if lit else bright,
                           font=(cfg.FONT_FAMILY, 12, "bold"))

    @staticmethod
    def _mix(color_a: str, color_b: str, ratio: float) -> str:
        """Két "#rrggbb" színt kever (ratio=0 -> az első, ratio=1 -> a második)."""
        a = [int(color_a[i:i + 2], 16) for i in (1, 3, 5)]
        b = [int(color_b[i:i + 2], 16) for i in (1, 3, 5)]
        mixed = [round(x + (y - x) * ratio) for x, y in zip(a, b)]
        return "#{:02x}{:02x}{:02x}".format(*mixed)

    def flash(self, index: int, duration: int | None = None) -> None:
        """A gombot rövid időre felvillantja, és megszólaltatja a hozzá tartozó hangot."""
        if duration is None:
            duration = self._timing()[0]
        self._draw_button(index, lit=True)
        self.play_tone(cfg.SIMON_TONES[index], duration)
        self._schedule(duration, self._draw_button, index, False)

    # ------------------------------------------------------------ játékmenet
    def on_color_click(self, index: int) -> None:
        """A játékos kattintása: ha éppen nyomhat, felvillantja és ellenőrzi."""
        if not self.accepting_input:
            return
        self.flash(index, 180)
        self.check_input(index)

    def check_input(self, index: int) -> None:
        """Összeveti a nyomott színt a sorozat soron következő elemével."""
        if index != self.sequence[self.player_pos]:
            self.game_over()
            return
        self.player_pos += 1
        if self.player_pos == len(self.sequence):    # az egész sorozatot eltalálta
            self.accepting_input = False
            self.status_label.config(text="Helyes!", fg=cfg.SUCCESS)
            self._schedule(260, self.play_melody, [(784, 80), (1047, 120)])
            self._schedule(1000, self.next_round)

    def game_over(self) -> None:
        """Hiba esetén vége: elmenti az elért szintet, és megmutatja az eredményt."""
        self.accepting_input = False
        completed = self.level - 1                   # a teljesített körök száma
        self.status_label.config(text="Hibás szín!", fg=cfg.DANGER)
        self.play_melody([(180, 250), (130, 400)])
        correct = self.sequence[self.player_pos]
        self._schedule(600, self.flash, correct, 400)     # megmutatja a helyes színt
        record = self.score_manager.add_simon_score(self.speed, completed)
        self.level_label.config(text=f"Elért szint: {completed}")
        self._update_best_label()
        self._schedule(1500, self._show_result, completed, record)

    def _show_result(self, completed: int, record: bool) -> None:
        """Az eredmény-panel megjelenítése."""
        self.show_overlay(
            "Játék vége",
            [f"Elért szint: {completed}", f"Sebesség: {self.speed}"],
            highlight="Új rekord!" if record else "",
        )

    def stop(self) -> None:
        """Megszakítja a folyamatban lévő időzített lépéseket."""
        self.accepting_input = False
        super().stop()

    # ------------------------------------------------------------ segédek
    def _category(self) -> str:
        """A ranglista kategóriája az aktuális sebességhez."""
        return f"simon_{self.speed}"

    def _set_speed(self, name: str) -> None:
        """Sebességváltás: új játékot indít."""
        self.speed = name
        self.new_game()

    def _update_best_label(self) -> None:
        """Kiírja az aktuális sebesség rekordját."""
        best = self.score_manager.get_best(self._category())
        self._best_label.config(text=f"Rekord: {best['level']}. szint" if best else "Rekord: –")

    def _on_sound_toggle(self) -> None:
        """Hang ki-be, és a gomb feliratának frissítése."""
        self.toggle_sound()
        if self._sound_button is not None:
            self._sound_button.config(text=self.sound_text())
