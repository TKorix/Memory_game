"""simon_game.py - a SimonGame osztály: a színsorozat-játék."""
import random
import tkinter as tk

import settings as cfg
from base_game import BaseGame, get_rank, mix_color, set_button_state


class SimonGame(BaseGame):
    """Simon: a program felvillant egy színsorozatot, a játékosnak vissza kell játszania.

    Minden helyes kör után a sorozat eggyel hosszabb lesz. Az első hibáig tart.
    """

    def __init__(self, root, score_manager, on_exit):
        super().__init__(root, score_manager, on_exit)
        self.speed = "Normál"               # a kiválasztott sebesség
        self.sequence = []                  # a megjegyzendő színek (0-3) sorrendben
        self.player_pos = 0                 # a játékos hányadiknál tart
        self.level = 0                      # az aktuális kör (= a sorozat hossza)
        self.accepting_input = False        # nyomhat-e most a játékos
        self.buttons = []                   # a négy színes gomb (tk.Button)
        self.level_label = None             # a szintet kiíró felirat
        self.status_label = None            # az üzenet ("Figyelj!", "Te jössz!")
        # ----- extrák
        self.flash_ms = 480                 # ennyi ideig világít egy szín
        self.dots_label = None              # a haladást mutató pontok
        self.best_label = None
        self.speed_buttons = {}

    def start(self):
        """Felépíti a felületet (build_ui), majd elindítja az első játékot (new_game)."""
        self.frame.pack(fill="both", expand=True)
        self.set_keys()
        for index in range(4):                          # az 1-4 billentyűk a színeknek
            self.root.bind(f"<Key-{index + 1}>", lambda event, i=index: self.on_color_click(i))
        self.build_ui()
        self.new_game()

    def build_ui(self):
        """Létrehozza a feliratokat, a sebességválasztót és a négy színes gombot."""
        self.best_label = self.make_header("Színsorozat")

        self.level_label = tk.Label(self.frame, bg=cfg.PANEL, fg=cfg.TEXT, width=26, pady=8,
                                    font=(cfg.FONT_FAMILY, 14, "bold"))
        self.level_label.pack(pady=(10, 2))
        self.status_label = tk.Label(self.frame, bg=cfg.BG, font=(cfg.FONT_FAMILY, 18, "bold"))
        self.status_label.pack()
        self.dots_label = tk.Label(self.frame, bg=cfg.BG, fg=cfg.MUTED,
                                   font=(cfg.SYMBOL_FONT, 13))
        self.dots_label.pack()

        options = tk.Frame(self.frame, bg=cfg.BG)
        options.pack(pady=(2, 0))
        self.speed_buttons = self.make_choice(options, "Sebesség:", cfg.SIMON_SPEEDS,
                                              self.change_speed)

        # a négy színes gomb 2x2-es rácsban
        pad = tk.Frame(self.frame, bg=cfg.BOARD_BG, padx=10, pady=10,
                       highlightbackground=cfg.BOARD_BORDER, highlightthickness=2)
        pad.pack(expand=True)
        self.buttons = []
        for index in range(4):
            button = self.make_tile(pad, cfg.SIMON_SIZE,
                                    lambda i=index: self.on_color_click(i), index // 2, index % 2)
            button.config(text=str(index + 1), font=(cfg.FONT_FAMILY, 20, "bold"))
            self.buttons.append(button)
            self.draw_button(index, False)

        self.make_bottom_bar("Esc: menü  ·  Szóköz: új játék  ·  1-4: színek  ·  M: hang")

    def new_game(self):
        """Kiüríti a sorozatot, nullázza a szintet, és elindítja az első kört."""
        self.cancel_all()
        self.hide_overlay()
        self.sequence = []
        self.player_pos = 0
        self.level = 0
        self.accepting_input = False
        for name, button in self.speed_buttons.items():
            set_button_state(button, name == self.speed)
        for index in range(4):
            self.draw_button(index, False)
        self.level_label.config(text="Szint: 0")
        self.status_label.config(text="Készülj!", fg=cfg.ACCENT_HI)
        self.dots_label.config(text="")
        self.update_best_label()
        self.later(700, self.next_round)

    def next_round(self):
        """Új véletlen színt tesz a sorozat végére, és lejátssza az egészet."""
        self.sequence.append(random.randrange(4))
        self.level += 1
        self.player_pos = 0
        self.level_label.config(text=f"Szint: {self.level}  ·  {get_rank(self.level)}")
        self.play_sequence()

    def play_sequence(self):
        """Letiltja a bevitelt, egymás után felvillantja a színeket, a végén engedélyezi a bevitelt."""
        self.accepting_input = False
        self.status_label.config(text="Figyelj!", fg=cfg.ACCENT_HI)
        self.update_dots()

        flash_ms, gap_ms = cfg.SIMON_SPEEDS[self.speed]
        self.flash_ms = max(cfg.SIMON_MIN_FLASH, flash_ms - self.level * cfg.SIMON_SPEEDUP)  # körönként gyorsul

        wait = 400
        for color in self.sequence:
            self.later(wait, self.flash, color)
            wait += self.flash_ms + gap_ms
        self.later(wait, self.enable_input)

    def enable_input(self):
        """A lejátszás után a játékos nyomhat."""
        self.accepting_input = True
        self.status_label.config(text="Te jössz!", fg=cfg.SUCCESS)

    def update_dots(self):
        """Pontokkal mutatja, hol tart a játékos (● kész, ○ hátra van)."""
        total = len(self.sequence)
        if total > 16:
            self.dots_label.config(text=f"{self.player_pos} / {total}")
        else:
            self.dots_label.config(text="● " * self.player_pos + "○ " * (total - self.player_pos))

    def flash(self, index):
        """Rövid időre felvillantja a gombot (világosabb szín), majd visszaállítja."""
        self.draw_button(index, True)
        self.play_tone(cfg.SIMON_TONES[index], self.flash_ms)
        self.later(self.flash_ms, self.draw_button, index, False)

    def draw_button(self, index, lit):
        """Beállítja a gomb színét (lit=True: éppen világít)."""
        normal, bright = cfg.SIMON_COLORS[index]
        if lit:
            back, text_color, border = bright, "#ffffff", "#ffffff"
        else:
            back, text_color, border = normal, bright, mix_color(normal, "#000000", 0.35)
        self.buttons[index].config(bg=back, activebackground=back, fg=text_color,
                                   activeforeground=text_color, highlightbackground=border,
                                   highlightcolor=border)

    def on_color_click(self, index):
        """A játékos megnyomott egy színt."""
        if not self.accepting_input:
            return
        self.flash(index)
        self.check_input(index)

    def check_input(self, index):
        """Megnézi, hogy a nyomott szín jó-e."""
        if index != self.sequence[self.player_pos]:
            self.game_over()
            return
        self.player_pos += 1
        self.update_dots()
        if self.player_pos == len(self.sequence):       # az egész sorozatot eltalálta
            self.accepting_input = False
            self.status_label.config(text=random.choice(["Helyes!", "Szép!", "Ügyes!", "Tovább!"]),
                                     fg=cfg.SUCCESS)
            self.later(250, self.play_melody, [(784, 100), (1047, 200)])
            self.later(1000, self.next_round)

    def game_over(self):
        """Hiba: elmenti az elért szintet, és megmutatja az eredményt."""
        self.accepting_input = False
        completed = self.level - 1                      # ennyi kört teljesített
        self.status_label.config(text="Hibás szín!", fg=cfg.DANGER)
        self.play_melody([(180, 300), (130, 450)])
        self.later(600, self.flash, self.sequence[self.player_pos])    # megmutatja a jó színt

        old_best = self.score_manager.get_best(self.category())
        record = self.score_manager.add_simon_score(self.speed, completed)
        self.level_label.config(text=f"Elért szint: {completed}")
        self.update_best_label()

        lines = [f"Rang: {get_rank(completed)}", f"Elért szint: {completed}  ·  {self.speed}"]
        if not record and old_best is not None:
            missing = old_best["level"] - completed + 1
            lines.append(f"A rekordod {old_best['level']}. szint – még {missing} kör kell hozzá!")
        self.later(1500, self.show_overlay, "Játék vége", lines, "Új rekord!" if record else "")

    def stop(self):
        """Megszakítja a folyamatban lévő időzített lépéseket (after_cancel)."""
        self.accepting_input = False
        super().stop()

    # ------------------------------------------------------------ kis segédek
    def category(self):
        """A ranglista kategóriája az aktuális sebességhez."""
        return "simon_" + self.speed

    def change_speed(self, name):
        """Sebesség váltása (új játék indul)."""
        self.speed = name
        self.new_game()

    def update_best_label(self):
        """Kiírja az aktuális sebesség rekordját."""
        best = self.score_manager.get_best(self.category())
        self.best_label.config(text=f"Rekord: {best['level']}. szint" if best else "Rekord: –")
