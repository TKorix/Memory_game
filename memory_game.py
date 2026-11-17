"""memory_game.py - a MemoryGame osztály: a kártyapár-kereső játék."""
import random
import tkinter as tk

import settings as cfg
from base_game import BaseGame, format_time, set_button_state, styled_button
from board import Board


class MemoryGame(BaseGame):
    """Kártyapár-kereső: két kártyát fordítunk fel, ha egyeznek, felfordítva maradnak."""

    def __init__(self, root, score_manager, on_exit):
        super().__init__(root, score_manager, on_exit)
        self.difficulty = "Közepes"     # a kiválasztott nehézségi szint
        self.board = None               # a pálya (Board objektum)
        self.buttons = []               # a kártyák (egy tk.Button = egy kártya)
        self.first_index = None         # az első felfordított kártya sorszáma
        self.locked = False             # igaz, amíg nem lehet kattintani
        self.moves = 0                  # lépések száma
        self.seconds = 0                # eltelt idő
        self.timer_running = False      # megy-e az óra
        self.moves_label = None         # a lépéseket kiíró felirat
        self.time_label = None          # az időt kiíró felirat
        # ----- extrák
        self.theme = "Jelek"            # mi legyen a kártyákon (Jelek / Betűk / Számok)
        self.streak = 0                 # hány találat volt egymás után (kombó)
        self.best_streak = 0            # a leghosszabb kombó ebben a játékban
        self.hints_left = 0             # hány segítség maradt
        self.hover = None               # melyik kártya fölött van az egér
        self.timer_id = None
        self.board_frame = None
        self.best_label = None
        self.info_label = None
        self.hint_button = None
        self.progress_bar = None
        self.level_buttons = {}
        self.theme_buttons = {}

    def start(self):
        """Felépíti a felületet (build_ui), majd elindítja az első játékot (new_game)."""
        self.frame.pack(fill="both", expand=True)
        self.set_keys()
        self.root.bind("<Key-h>", lambda event: self.use_hint())
        self.build_ui()
        self.new_game()

    def build_ui(self):
        """Létrehozza a feliratokat, a gombokat és a kártyák helyét."""
        self.best_label = self.make_header("Kártyapár-kereső")

        # lépések, idő, segítség
        stats = tk.Frame(self.frame, bg=cfg.BG)
        stats.pack(pady=(10, 4))
        self.moves_label = tk.Label(stats, bg=cfg.PANEL, fg=cfg.TEXT, width=22, pady=8,
                                    font=(cfg.FONT_FAMILY, 14, "bold"))
        self.moves_label.pack(side="left", padx=6)
        self.time_label = tk.Label(stats, bg=cfg.PANEL, fg=cfg.TEXT, width=12, pady=8,
                                   font=(cfg.FONT_FAMILY, 14, "bold"))
        self.time_label.pack(side="left", padx=6)
        self.hint_button = styled_button(stats, "", self.use_hint, pady=8)
        self.hint_button.pack(side="left", padx=6)

        # haladássáv (annyira telik meg, ahány pár megvan)
        track = tk.Frame(self.frame, bg=cfg.PANEL_HI, width=440, height=6)
        track.pack(pady=(2, 0))
        self.progress_bar = tk.Frame(track, bg=cfg.SUCCESS)
        self.progress_bar.place(x=0, y=0, relheight=1.0, relwidth=0.0)

        self.info_label = tk.Label(self.frame, bg=cfg.BG, font=(cfg.FONT_FAMILY, 13, "bold"))
        self.info_label.pack(pady=(4, 0))

        # nehézség- és témaválasztó
        options = tk.Frame(self.frame, bg=cfg.BG)
        options.pack(pady=(2, 0))
        self.level_buttons = self.make_choice(options, "Nehézség:", cfg.DIFFICULTIES,
                                              self.change_difficulty)
        self.theme_buttons = self.make_choice(options, "Téma:", cfg.THEMES, self.change_theme)

        self.board_frame = tk.Frame(self.frame, bg=cfg.BOARD_BG, padx=12, pady=12,
                                    highlightbackground=cfg.BOARD_BORDER, highlightthickness=2)
        self.board_frame.pack(expand=True)

        self.make_bottom_bar("Esc: menü  ·  Szóköz: új játék  ·  H: segítség  ·  M: hang")

    def new_game(self):
        """Új pályát csinál, nullázza a számlálókat, és megmutatja a kártyákat."""
        self.cancel_all()
        self.hide_overlay()
        rows, cols = cfg.DIFFICULTIES[self.difficulty]
        self.board = Board(rows, cols, cfg.THEMES[self.theme])
        self.first_index = None
        self.moves = 0
        self.seconds = 0
        self.streak = 0
        self.best_streak = 0
        self.hints_left = cfg.HINTS_PER_GAME
        self.timer_running = False
        self.hover = None
        for name, button in self.level_buttons.items():
            set_button_state(button, name == self.difficulty)
        for name, button in self.theme_buttons.items():
            set_button_state(button, name == self.theme)
        self.draw_board()
        self.update_labels()
        self.update_best_label()
        self.show_preview()

    def show_preview(self):
        """Pár másodpercre felfordítja az összes kártyát, hogy meg lehessen jegyezni őket."""
        self.locked = True
        self.info_label.config(text="Jegyezd meg a kártyákat!", fg=cfg.GOLD)
        for index, card in enumerate(self.board.cards):
            card.flip()
            self.update_card_button(index)
        self.later(cfg.PREVIEW_MS[self.difficulty], self.end_preview)

    def end_preview(self):
        """Lefordítja a kártyákat, és kezdődhet a játék."""
        for index, card in enumerate(self.board.cards):
            card.hide()
            self.flip_animation(index)
        self.locked = False
        self.info_label.config(text="Találd meg a párokat!", fg=cfg.ACCENT_HI)
        self.play_tone(440, 160)

    def draw_board(self):
        """Létrehozza a kártyagombokat rácsban."""
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.buttons = []
        size = cfg.CARD_SIZES[self.difficulty]
        for index in range(len(self.board.cards)):
            row, col = divmod(index, self.board.cols)
            button = self.make_tile(self.board_frame, size,
                                    lambda i=index: self.on_card_click(i), row, col)
            button.config(font=(cfg.SYMBOL_FONT, int(size * 0.36), "bold"))
            button.bind("<Enter>", lambda event, i=index: self.on_hover(i))
            button.bind("<Leave>", lambda event: self.on_hover(None))
            self.buttons.append(button)
            self.update_card_button(index)

    def update_card_button(self, index):
        """A kártya állapota szerint beállítja a gomb színét és szövegét."""
        button = self.buttons[index]
        card = self.board.get_card(index)
        if card.is_face_up:
            # felfordítva: a szimbólum a saját színével (a megtalált pár zöld hátterű)
            color = cfg.SYMBOL_COLORS[cfg.THEMES[self.theme].index(card.value)]
            if card.is_matched:
                back, border = cfg.CARD_MATCHED, cfg.SUCCESS
            else:
                back, border = cfg.CARD_FACE, cfg.ACCENT_HI
            text = card.value
        else:
            # lefordítva (ha fölötte az egér, világosabb)
            hovered = (index == self.hover)
            back = cfg.CARD_BACK_HI if hovered else cfg.CARD_BACK
            border = cfg.ACCENT if hovered else cfg.CARD_BORDER
            color = cfg.CARD_PATTERN
            text = "◆"
        button.config(text=text, fg=color, bg=back, activeforeground=color,
                      activebackground=back, highlightbackground=border, highlightcolor=border)

    def on_hover(self, index):
        """Az egér fölé érésekor kiemeli a lefordított kártyát."""
        old = self.hover
        self.hover = index
        for i in (old, index):
            if i is not None and i < len(self.buttons):
                if not self.board.get_card(i).is_face_up:
                    self.update_card_button(i)

    def flip_animation(self, index, step=0):
        """Fordítás animáció: a kártya összeszűkül, a közepén átvált, majd kinyílik."""
        if index >= len(self.buttons):
            return
        scale = max(abs(1 - step / 4), 0.05)            # a szélesség: 1 -> 0 -> 1
        self.buttons[index].place_configure(relwidth=scale)
        if step == 4:
            self.update_card_button(index)              # a közepén mutatjuk a másik oldalát
        if step < 8:
            self.later(20, self.flip_animation, index, step + 1)

    def on_card_click(self, index):
        """Egy kártyára kattintottak."""
        card = self.board.get_card(index)
        if self.locked or card.is_face_up:
            return

        if not self.timer_running:                      # az első kattintásra indul az óra
            self.timer_running = True
            self.timer_id = self.later(1000, self.tick)

        card.flip()
        self.flip_animation(index)
        self.play_tone(700, 50)

        if self.first_index is None:
            self.first_index = index                    # ez az első kártya
        else:
            self.moves += 1                             # a másodikkal egy lépés kész
            self.update_labels()
            self.check_pair(self.first_index, index)

    def check_pair(self, first, second):
        """Megnézi, hogy a két felfordított kártya egyezik-e."""
        self.first_index = None
        card_a = self.board.get_card(first)
        card_b = self.board.get_card(second)

        if card_a.matches(card_b):
            card_a.set_matched()
            card_b.set_matched()
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            if self.streak >= 2:
                self.info_label.config(text=f"Kombó ×{self.streak}!", fg=cfg.GOLD)
            else:
                self.info_label.config(text="Találat!", fg=cfg.SUCCESS)
            high = min(self.streak, 6) * 90             # a kombóval egyre magasabb a hang
            self.play_melody([(560 + high, 110), (840 + high, 260)])
            self.later(200, self.update_card_button, first)
            self.later(200, self.update_card_button, second)
            self.update_labels()
            if self.board.is_finished():
                self.locked = True
                self.later(700, self.finish_game)
        else:
            self.streak = 0
            self.info_label.config(text="Nem egyezik – próbáld újra!", fg=cfg.MUTED)
            self.locked = True
            self.later(cfg.MISMATCH_DELAY, self.hide_mismatch, first, second)

    def hide_mismatch(self, first, second):
        """Visszafordítja a nem egyező kártyákat, és feloldja a zárolást."""
        self.play_tone(200, 220)
        for index in (first, second):
            self.board.get_card(index).hide()
            self.flip_animation(index)
        self.locked = False

    def use_hint(self):
        """Segítség: egy másodpercre megmutat egy párt (2 lépésbe kerül)."""
        if self.locked or self.first_index is not None or self.hints_left == 0:
            return
        places = {}                                     # szimbólum -> hol van a két kártya
        for index, card in enumerate(self.board.cards):
            if not card.is_matched:
                places.setdefault(card.value, []).append(index)
        first, second = random.choice(list(places.values()))
        self.hints_left -= 1
        self.moves += 2
        self.locked = True
        for index in (first, second):
            self.board.get_card(index).flip()
            self.flip_animation(index)
        self.later(1200, self.end_hint, first, second)
        self.update_labels()

    def end_hint(self, first, second):
        """A segítség után visszafordítja a két kártyát."""
        for index in (first, second):
            self.board.get_card(index).hide()
            self.flip_animation(index)
        self.locked = False

    def tick(self):
        """Másodpercenként növeli az időt, amíg megy az óra."""
        if self.timer_running:
            self.seconds += 1
            self.update_labels()
            self.timer_id = self.later(1000, self.tick)

    def update_labels(self):
        """Kiírja a lépéseket, a megtalált párokat, az időt és a segítségek számát."""
        found = 0
        for card in self.board.cards:
            if card.is_matched:
                found += 1
        pairs = self.board.pair_count()
        self.moves_label.config(text=f"Lépés: {self.moves}  ·  Pár: {found // 2}/{pairs}")
        self.time_label.config(text=f"Idő: {format_time(self.seconds)}")
        self.hint_button.config(text=f"Segítség ({self.hints_left})")
        self.progress_bar.place_configure(relwidth=(found // 2) / pairs)

    def finish_game(self):
        """Vége: leállítja az órát, elmenti az eredményt, megmutatja a végeredményt."""
        self.timer_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        old_best = self.score_manager.get_best(self.category())
        record = self.score_manager.add_memory_score(self.difficulty, self.moves, self.seconds)

        # csillagok: minél kevesebb a lépés, annál több
        pairs = self.board.pair_count()
        if self.moves <= pairs * 1.5:
            stars = 3
        elif self.moves <= pairs * 2.2:
            stars = 2
        else:
            stars = 1

        lines = [cfg.MEMORY_RANKS[stars],
                 f"{self.moves} lépés  ·  {format_time(self.seconds)}",
                 f"Leghosszabb kombó: ×{self.best_streak}"]
        if not record and old_best is not None:
            lines.append(f"A rekordod {old_best['moves']} lépés – döntsd meg!")

        self.play_melody([(523, 130), (659, 130), (784, 130), (1047, 450)])
        self.update_best_label()
        self.show_overlay("Gratulálunk!", lines, "Új rekord!" if record else "",
                          "★" * stars + "☆" * (3 - stars))

    def stop(self):
        """Leállítja az órát és az időzítőket."""
        self.timer_running = False
        super().stop()

    # ------------------------------------------------------------ kis segédek
    def category(self):
        """A ranglista kategóriája az aktuális nehézséghez."""
        return "memory_" + self.difficulty

    def change_difficulty(self, name):
        """Nehézség váltása (új játék indul)."""
        self.difficulty = name
        self.new_game()

    def change_theme(self, name):
        """Téma váltása (új játék indul)."""
        self.theme = name
        self.new_game()

    def update_best_label(self):
        """Kiírja az aktuális nehézség rekordját."""
        best = self.score_manager.get_best(self.category())
        if best:
            text = f"Rekord: {best['moves']} lépés · {format_time(best['seconds'])}"
        else:
            text = "Rekord: –"
        self.best_label.config(text=text)
