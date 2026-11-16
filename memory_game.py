"""memory_game.py - a MemoryGame osztály: a kártyapár-kereső játékmód."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

import settings as cfg
from base_game import BaseGame, format_time, rounded_rect, set_button_state, styled_button
from board import Board


class MemoryGame(BaseGame):
    """Kártyapár-kereső: két kártyát kell felfordítani, az egyezők megmaradnak."""

    def __init__(self, root: tk.Tk, score_manager, on_exit: Callable) -> None:
        super().__init__(root, score_manager, on_exit)
        self.difficulty: str = "Közepes"            # a kiválasztott nehézségi szint
        self.board: Board | None = None             # az aktuális pálya
        self.buttons: list[tk.Canvas] = []          # egy vászon = egy kártya
        self.first_index: int | None = None         # az első felfordított kártya indexe
        self.locked: bool = False                   # igaz, amíg a rossz páros látszik
        self.moves: int = 0                         # lépések száma
        self.seconds: int = 0                       # eltelt idő
        self.timer_running: bool = False            # fut-e az időmérő
        self.moves_label: tk.Label | None = None
        self.time_label: tk.Label | None = None
        # belső segédek
        self._timer_id: str | None = None
        self._hover_index: int | None = None
        self._board_frame: tk.Frame | None = None
        self._difficulty_buttons: dict[str, tk.Label] = {}
        self._best_label: tk.Label | None = None
        self._sound_button: tk.Label | None = None

    # ----------------------------------------------------------- indítás
    def start(self) -> None:
        """Megjeleníti a játék keretét, felépíti a felületet és elindítja az első játékot."""
        self.frame.pack(fill="both", expand=True)
        self.bind_key("<Escape>", lambda event: self.back_to_menu())
        self.bind_key("<space>", lambda event: self.new_game())
        self.bind_key("<Key-m>", lambda event: self._on_sound_toggle())
        self.build_ui()
        self.new_game()

    def build_ui(self) -> None:
        """Létrehozza a címet, a számlálókat, a gombokat és a pálya helyét."""
        header = tk.Frame(self.frame, bg=cfg.BG)
        header.pack(fill="x", padx=30, pady=(22, 4))
        tk.Label(header, text="Kártyapár-kereső", bg=cfg.BG, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 24, "bold")).pack(side="left")
        self._best_label = tk.Label(header, text="", bg=cfg.BG, fg=cfg.MUTED,
                                    font=(cfg.FONT_FAMILY, 11))
        self._best_label.pack(side="right")

        # Számlálók
        stats = tk.Frame(self.frame, bg=cfg.BG)
        stats.pack(pady=(10, 4))
        self.moves_label = tk.Label(stats, bg=cfg.PANEL, fg=cfg.TEXT, width=14, pady=8,
                                    font=(cfg.FONT_FAMILY, 14, "bold"))
        self.moves_label.pack(side="left", padx=8)
        self.time_label = tk.Label(stats, bg=cfg.PANEL, fg=cfg.TEXT, width=14, pady=8,
                                   font=(cfg.FONT_FAMILY, 14, "bold"))
        self.time_label.pack(side="left", padx=8)

        # Nehézségválasztó
        levels = tk.Frame(self.frame, bg=cfg.BG)
        levels.pack(pady=(8, 0))
        tk.Label(levels, text="Nehézség:", bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 11)).pack(side="left", padx=(0, 8))
        for name in cfg.DIFFICULTIES:
            button = styled_button(levels, name, lambda n=name: self._set_difficulty(n),
                                   font_size=10, padx=14, pady=5)
            button.pack(side="left", padx=4)
            self._difficulty_buttons[name] = button

        # A pálya helye
        self._board_frame = tk.Frame(self.frame, bg=cfg.BG)
        self._board_frame.pack(expand=True)

        # Alsó gombsor
        bottom = tk.Frame(self.frame, bg=cfg.BG)
        bottom.pack(pady=(0, 6))
        styled_button(bottom, "Új játék", self.new_game, primary=True).pack(side="left", padx=5)
        styled_button(bottom, "Ranglista",
                      lambda: self.show_scores(self._category())).pack(side="left", padx=5)
        self._sound_button = styled_button(bottom, self.sound_text(), self._on_sound_toggle)
        self._sound_button.pack(side="left", padx=5)
        styled_button(bottom, "Vissza a menübe", self.back_to_menu).pack(side="left", padx=5)
        tk.Label(self.frame, text="Esc: menü  ·  Szóköz: új játék  ·  M: hang",
                 bg=cfg.BG, fg=cfg.MUTED, font=(cfg.FONT_FAMILY, 9)).pack(pady=(0, 12))

    # --------------------------------------------------------- új játék
    def new_game(self) -> None:
        """Új pályát hoz létre a kiválasztott szint szerint, és nullázza a számlálókat."""
        self._cancel_scheduled()
        self.hide_overlay()
        rows, cols = cfg.DIFFICULTIES[self.difficulty]
        self.board = Board(rows, cols, cfg.SYMBOLS)
        self.first_index = None
        self.locked = False
        self.moves = 0
        self.seconds = 0
        self.timer_running = False
        self._timer_id = None
        self._hover_index = None
        for name, button in self._difficulty_buttons.items():
            set_button_state(button, name == self.difficulty)
        self.draw_board()
        self.update_labels()
        self._update_best_label()

    def draw_board(self) -> None:
        """Létrehozza a kártyákat (vásznakat) rácsban a pálya mérete szerint."""
        for widget in self._board_frame.winfo_children():
            widget.destroy()
        self.buttons = []
        size = cfg.CARD_SIZES[self.difficulty]
        for index in range(len(self.board.cards)):
            canvas = tk.Canvas(self._board_frame, width=size, height=size, bg=cfg.BG,
                               highlightthickness=0, cursor="hand2")
            row, col = divmod(index, self.board.cols)
            canvas.grid(row=row, column=col, padx=5, pady=5)
            canvas.bind("<Button-1>", lambda event, i=index: self.on_card_click(i))
            canvas.bind("<Enter>", lambda event, i=index: self._on_hover(i, True))
            canvas.bind("<Leave>", lambda event, i=index: self._on_hover(i, False))
            self.buttons.append(canvas)
            self.update_card_button(index)

    # ---------------------------------------------------- kártya megjelenítés
    def update_card_button(self, index: int) -> None:
        """A kártya aktuális állapota szerint újrarajzolja a vásznát."""
        self._draw_card(index)

    def _draw_card(self, index: int, scale: float = 1.0, show_face: bool | None = None,
                   glow: bool = False) -> None:
        """Lerajzolja a kártyát. A scale < 1 a fordítás animációjához kell."""
        canvas = self.buttons[index]
        card = self.board.get_card(index)
        size = cfg.CARD_SIZES[self.difficulty]
        if show_face is None:
            show_face = card.is_face_up or card.is_matched

        canvas.delete("all")
        center = size / 2
        half = (size / 2 - 6) * scale          # a vízszintes "összeszűkülés"
        x0, x1 = center - half, center + half
        y0, y1 = 6, size - 6
        radius = size * 0.12

        rounded_rect(canvas, x0 + 2, y0 + 4, x1 + 2, y1 + 4, radius,
                     fill=cfg.SHADOW, outline="")                    # árnyék

        if show_face:
            if card.is_matched:
                fill, outline, width = cfg.CARD_MATCHED, cfg.SUCCESS, 4 if glow else 3
            else:
                fill, outline, width = cfg.CARD_FACE, cfg.ACCENT_HI, 2
            rounded_rect(canvas, x0, y0, x1, y1, radius, fill=fill, outline=outline, width=width)
            if scale > 0.5:
                symbol_index = cfg.SYMBOLS.index(card.value) if card.value in cfg.SYMBOLS else 0
                color = cfg.SYMBOL_COLORS[symbol_index % len(cfg.SYMBOL_COLORS)]
                canvas.create_text(center, center + 2, text=card.value, fill=color,
                                   font=(cfg.SYMBOL_FONT, int(size * 0.44)))
        else:
            hovered = index == self._hover_index
            fill = cfg.CARD_BACK_HI if hovered else cfg.CARD_BACK
            outline = cfg.ACCENT if hovered else cfg.CARD_BORDER
            rounded_rect(canvas, x0, y0, x1, y1, radius, fill=fill, outline=outline, width=2)
            if scale > 0.5:
                # a kártyahát mintája: egy rombusz
                d = size * 0.17 * scale
                canvas.create_polygon(center, center - d, center + d, center, center, center + d,
                                      center - d, center, fill=cfg.CARD_PATTERN, outline="")

    def _on_hover(self, index: int, inside: bool) -> None:
        """Az egér fölé érésekor kiemeli a lefordított kártyát."""
        if self.board is None or index >= len(self.buttons):
            return
        self._hover_index = index if inside else None
        card = self.board.get_card(index)
        if not card.is_face_up and not card.is_matched:
            self.update_card_button(index)

    def _animate_flip(self, index: int, to_face: bool, step: int = 0) -> None:
        """A kártyafordítás animációja: összeszűkül, majd kinyílik a másik oldalával."""
        if index >= len(self.buttons):
            return
        if step > cfg.FLIP_STEPS:
            self.update_card_button(index)
            return
        progress = step / cfg.FLIP_STEPS
        scale = max(abs(1 - 2 * progress), 0.04)
        show_face = to_face if progress >= 0.5 else not to_face
        self._draw_card(index, scale, show_face)
        self._schedule(cfg.FLIP_STEP_MS, self._animate_flip, index, to_face, step + 1)

    def _pulse(self, indices: list[int], step: int = 0) -> None:
        """A megtalált pár rövid, villogó kiemelése."""
        if step > 5:
            for index in indices:
                self.update_card_button(index)
            return
        for index in indices:
            self._draw_card(index, glow=step % 2 == 0)
        self._schedule(90, self._pulse, indices, step + 1)

    # ------------------------------------------------------------ játékmenet
    def on_card_click(self, index: int) -> None:
        """Egy kártyára kattintás kezelése."""
        if self.locked or self.board is None:
            return
        card = self.board.get_card(index)
        if card.is_face_up or card.is_matched:
            return                                   # már fel van fordítva

        if not self.timer_running:                   # az első kattintásra indul az idő
            self.timer_running = True
            self._timer_id = self._schedule(1000, self.tick)

        card.flip()
        self._animate_flip(index, True)
        self.play_tone(660, 35)

        if self.first_index is None:
            self.first_index = index                 # ez volt az első kártya
        else:
            self.moves += 1                          # a második kártyával egy lépés kész
            self.update_labels()
            self.check_pair(self.first_index, index)

    def check_pair(self, first: int, second: int) -> None:
        """Összehasonlítja a két felfordított kártyát."""
        self.first_index = None
        card_a = self.board.get_card(first)
        card_b = self.board.get_card(second)

        if card_a.matches(card_b):
            card_a.set_matched()
            card_b.set_matched()
            flip_time = (cfg.FLIP_STEPS + 1) * cfg.FLIP_STEP_MS
            self._schedule(flip_time, self._pulse, [first, second])
            self.play_melody([(784, 70), (988, 90)])
            if self.board.is_finished():
                self.locked = True
                self._schedule(flip_time + 700, self.finish_game)
        else:
            self.locked = True                       # amíg a rossz páros látszik, nem kattinthatunk
            self._schedule(cfg.MISMATCH_DELAY, self.hide_mismatch, first, second)

    def hide_mismatch(self, first: int, second: int) -> None:
        """Visszafordítja a nem egyező két kártyát, majd feloldja a zárolást."""
        self.play_tone(220, 90)
        for index in (first, second):
            self.board.get_card(index).hide()
            self._animate_flip(index, False)
        unlock_time = (cfg.FLIP_STEPS + 2) * cfg.FLIP_STEP_MS
        self._schedule(unlock_time, self._unlock)

    def _unlock(self) -> None:
        """Feloldja a zárolást (a fordítási animáció után)."""
        self.locked = False

    def tick(self) -> None:
        """Másodpercenként növeli az időt, amíg az időmérő fut."""
        if not self.timer_running:
            return
        self.seconds += 1
        self.update_labels()
        self._timer_id = self._schedule(1000, self.tick)

    def update_labels(self) -> None:
        """Kiírja a lépésszámot és az időt."""
        self.moves_label.config(text=f"Lépések: {self.moves}")
        self.time_label.config(text=f"Idő: {format_time(self.seconds)}")

    def finish_game(self) -> None:
        """Leállítja az időt, elmenti az eredményt, és megmutatja a végeredményt."""
        self.timer_running = False
        self._cancel(self._timer_id)
        record = self.score_manager.add_memory_score(self.difficulty, self.moves, self.seconds)
        self.play_melody([(523, 120), (659, 120), (784, 120), (1047, 300)])
        self._update_best_label()
        self.show_overlay(
            "Gratulálunk!",
            [f"{self.moves} lépés  ·  {format_time(self.seconds)}", f"Nehézség: {self.difficulty}"],
            highlight="Új rekord!" if record else "",
        )

    def stop(self) -> None:
        """Leállítja az időmérőt és az animációkat."""
        self.timer_running = False
        super().stop()

    # ------------------------------------------------------------ segédek
    def _category(self) -> str:
        """A ranglista kategóriája az aktuális szinthez."""
        return f"memory_{self.difficulty}"

    def _set_difficulty(self, name: str) -> None:
        """Nehézségi szint váltása: új játékot indít."""
        self.difficulty = name
        self.new_game()

    def _update_best_label(self) -> None:
        """Kiírja az aktuális szint rekordját."""
        best = self.score_manager.get_best(self._category())
        if best:
            text = f"Rekord: {best['moves']} lépés · {format_time(best['seconds'])}"
        else:
            text = "Rekord: –"
        self._best_label.config(text=text)

    def _on_sound_toggle(self) -> None:
        """Hang ki-be, és a gomb feliratának frissítése."""
        self.toggle_sound()
        if self._sound_button is not None:
            self._sound_button.config(text=self.sound_text())
