"""base_game.py - a BaseGame ősosztály, amiből a két játék származik.

Ami mindkét játékban ugyanaz (fejléc, gombok, hang, időzítők, eredménypanel,
ranglista), az itt van, így csak egyszer kellett megírni.
"""
import io
import math
import struct
import threading
import tkinter as tk
import wave

import settings as cfg

try:
    import winsound      # ez csak Windowson van meg
except ImportError:
    winsound = None


# ------------------------------------------------------------ kis segédfüggvények
def format_time(seconds):
    """75 másodpercből "01:15" lesz."""
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def mix_color(color_a, color_b, ratio):
    """Két színt kever (ratio=0: az első szín, ratio=1: a második)."""
    a = [int(color_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(color_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#{:02x}{:02x}{:02x}".format(*[round(x + (y - x) * ratio) for x, y in zip(a, b)])


def rounded_rect(canvas, x0, y0, x1, y1, radius, **options):
    """Lekerekített téglalapot rajzol."""
    radius = max(0, min(radius, (x1 - x0) / 2, (y1 - y0) / 2))
    points = [x0 + radius, y0, x1 - radius, y0, x1, y0, x1, y0 + radius,
              x1, y1 - radius, x1, y1, x1 - radius, y1, x0 + radius, y1,
              x0, y1, x0, y1 - radius, x0, y0 + radius, x0, y0]
    return canvas.create_polygon(points, smooth=True, **options)


def styled_button(parent, text, command, primary=False, font_size=11, padx=18, pady=8):
    """Szép gomb (egy Label, amire kattintva lefut a command)."""
    label = tk.Label(parent, text=text, fg=cfg.TEXT, cursor="hand2", padx=padx, pady=pady,
                     font=(cfg.FONT_FAMILY, font_size, "bold"))
    set_button_state(label, primary)
    label.bind("<Enter>", lambda event: label.config(bg=label.hover_color))
    label.bind("<Leave>", lambda event: label.config(bg=label.base_color))
    label.bind("<Button-1>", lambda event: command())
    return label


def set_button_state(label, active):
    """Kiemelt (active=True) vagy sima színű lesz a gomb."""
    label.base_color = cfg.ACCENT if active else cfg.PANEL_HI
    label.hover_color = cfg.ACCENT_HI if active else cfg.BUTTON_HOVER
    label.config(bg=label.base_color)


def get_rank(level):
    """A Simon szintjéhez tartozó címet adja vissza (pl. 9. szint -> "Haladó")."""
    title = cfg.RANKS[0][1]
    for needed_level, name in cfg.RANKS:
        if level >= needed_level:
            title = name
    return title


def make_wav(frequency, ms):
    """Egy hangot készít szinuszhullámból a memóriában (nincs szükség hangfájlra)."""
    rate = cfg.SAMPLE_RATE
    count = int(rate * ms / 1000)
    samples = []
    for i in range(count):
        fade_in = min(1.0, i / 100)                 # puha indulás
        fade_out = math.exp(-5 * i / count)         # lassú lecsengés
        value = (math.sin(2 * math.pi * frequency * i / rate)
                 + 0.3 * math.sin(4 * math.pi * frequency * i / rate))
        samples.append(int(value * fade_in * fade_out * 12000 * cfg.SOUND_VOLUME))

    stream = io.BytesIO()
    with wave.open(stream, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(struct.pack("<%dh" % count, *samples))
    return stream.getvalue()


# ------------------------------------------------------------ BaseGame
class BaseGame:
    """A két játék közös őse."""

    sound_enabled = cfg.SOUND_ENABLED     # a hang ki-be kapcsolása mindkét játékra érvényes

    def __init__(self, root, score_manager, on_exit):
        self.root = root                          # a főablak
        self.score_manager = score_manager        # a ranglistát kezelő objektum
        self.on_exit = on_exit                    # ezt hívjuk, ha vissza kell lépni a menübe
        self.frame = tk.Frame(root, bg=cfg.BG)    # a játék saját kerete
        self.timers = []                          # a várakozó időzítők listája
        self.overlay = None                       # az eredménypanel (ha éppen látszik)
        self.sound_button = None                  # a hang gomb

    def start(self):
        """A játékok felülírják: felépítik a felületet és elindítják a játékot."""
        raise NotImplementedError

    def new_game(self):
        """A játékok felülírják: új játékot indítanak."""
        raise NotImplementedError

    def category(self):
        """A játékok felülírják: a ranglista kategóriáját adják vissza."""
        raise NotImplementedError

    def stop(self):
        """Leállítja az időzítőket, és leveszi a billentyűparancsokat."""
        self.cancel_all()
        for key in ("<Escape>", "<space>", "<Key-m>", "<Key-h>", "<Key-1>", "<Key-2>", "<Key-3>", "<Key-4>"):
            self.root.unbind(key)

    # ------------------------------------------------------------ időzítők
    def later(self, ms, function, *arguments):
        """Ennyi ezredmásodperc múlva meghívja a függvényt."""
        timer = self.root.after(ms, function, *arguments)
        self.timers.append(timer)
        return timer

    def cancel_all(self):
        """Az összes várakozó időzítőt megszakítja."""
        for timer in self.timers:
            self.root.after_cancel(timer)
        self.timers = []

    # ------------------------------------------------------------ hang
    def play_melody(self, notes):
        """Hangokat játszik egymás után. notes: (frekvencia, hossz ms) párok listája.

        Külön szálon fut, hogy a játék ne akadjon meg. Csak Windowson szól.
        """
        if not BaseGame.sound_enabled or winsound is None:
            return

        def play():
            try:
                for frequency, ms in notes:
                    winsound.PlaySound(make_wav(frequency, ms), winsound.SND_MEMORY)
            except Exception:
                pass    # ha a hang nem megy, a játék csendben fut tovább

        threading.Thread(target=play, daemon=True).start()

    def play_tone(self, frequency, ms):
        """Egyetlen hangot játszik le."""
        self.play_melody([(frequency, ms)])

    def sound_text(self):
        """A hang gomb felirata."""
        return "Hang: be" if BaseGame.sound_enabled else "Hang: ki"

    def change_sound(self):
        """Hang ki-be."""
        BaseGame.sound_enabled = not BaseGame.sound_enabled
        if self.sound_button is not None:
            self.sound_button.config(text=self.sound_text())

    # ------------------------------------------------------------ közös felület
    def make_header(self, title):
        """Fejlécsáv a játék címével és a rekorddal. A rekord feliratát adja vissza."""
        bar = tk.Frame(self.frame, bg=cfg.PANEL)
        bar.pack(fill="x")
        tk.Label(bar, text=title, bg=cfg.PANEL, fg=cfg.TEXT, padx=24, pady=10,
                 font=(cfg.FONT_FAMILY, 22, "bold")).pack(side="left")
        best_label = tk.Label(bar, bg=cfg.PANEL, fg=cfg.GOLD, padx=24,
                              font=(cfg.FONT_FAMILY, 12, "bold"))
        best_label.pack(side="right")
        tk.Frame(self.frame, bg=cfg.ACCENT, height=3).pack(fill="x")
        return best_label

    def make_choice(self, parent, text, names, command):
        """Választógombok sora (pl. nehézségek). Egy {név: gomb} szótárat ad vissza."""
        tk.Label(parent, text=text, bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 11)).pack(side="left", padx=(14, 6))
        buttons = {}
        for name in names:
            button = styled_button(parent, name, lambda n=name: command(n),
                                   font_size=10, padx=12, pady=4)
            button.pack(side="left", padx=3)
            buttons[name] = button
        return buttons

    def make_tile(self, parent, size, command, row, column):
        """Egy négyzet alakú gombot (tk.Button) tesz a rácsba. A gombot adja vissza.

        A gomb egy fix méretű keretben van, így a szélessége animálható (kártyafordítás).
        """
        cell = tk.Frame(parent, width=size, height=size, bg=cfg.BOARD_BG)
        cell.grid(row=row, column=column, padx=5, pady=5)
        button = tk.Button(cell, bd=0, relief="flat", cursor="hand2", takefocus=0,
                           highlightthickness=4, command=command)
        button.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)
        return button

    def make_bottom_bar(self, hint):
        """Alsó gombsor (Új játék, Ranglista, Hang, Vissza) és a billentyűk tippje."""
        bar = tk.Frame(self.frame, bg=cfg.BG)
        bar.pack(pady=(4, 0))
        styled_button(bar, "Új játék", self.new_game, primary=True).pack(side="left", padx=5)
        styled_button(bar, "Ranglista",
                      lambda: self.show_scores(self.category())).pack(side="left", padx=5)
        self.sound_button = styled_button(bar, self.sound_text(), self.change_sound)
        self.sound_button.pack(side="left", padx=5)
        styled_button(bar, "Vissza a menübe", self.back_to_menu).pack(side="left", padx=5)
        tk.Label(self.frame, text=hint, bg=cfg.BG, fg=cfg.MUTED,
                 font=(cfg.FONT_FAMILY, 9)).pack(pady=(4, 8))

    def set_keys(self):
        """Billentyűk: Esc = menü, szóköz = új játék, M = hang."""
        self.root.bind("<Escape>", lambda event: self.back_to_menu())
        self.root.bind("<space>", lambda event: self.new_game())
        self.root.bind("<Key-m>", lambda event: self.change_sound())

    # ------------------------------------------------------------ eredménypanel
    def show_overlay(self, title, lines, highlight="", stars=""):
        """A játék közepére eredménypanelt tesz Új játék és Főmenü gombbal."""
        self.hide_overlay()
        box = tk.Frame(self.frame, bg=cfg.PANEL, padx=44, pady=26,
                       highlightbackground=cfg.ACCENT, highlightthickness=2)
        tk.Label(box, text=title, bg=cfg.PANEL, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 26, "bold")).pack()
        if stars:
            tk.Label(box, text=stars, bg=cfg.PANEL, fg=cfg.GOLD,
                     font=(cfg.SYMBOL_FONT, 30)).pack(pady=(4, 0))
        if highlight:
            tk.Label(box, text=f"  {highlight}  ", bg=cfg.SUCCESS, fg=cfg.BG, pady=2,
                     font=(cfg.FONT_FAMILY, 12, "bold")).pack(pady=(8, 0))
        for line in lines:
            tk.Label(box, text=line, bg=cfg.PANEL, fg=cfg.MUTED,
                     font=(cfg.FONT_FAMILY, 13)).pack(pady=(6, 0))
        buttons = tk.Frame(box, bg=cfg.PANEL)
        buttons.pack(pady=(22, 0))
        styled_button(buttons, "Új játék", self.new_game, primary=True).pack(side="left", padx=6)
        styled_button(buttons, "Főmenü", self.back_to_menu).pack(side="left", padx=6)
        box.place(relx=0.5, rely=0.5, anchor="center")
        self.overlay = box

    def hide_overlay(self):
        """Eltünteti az eredménypanelt."""
        if self.overlay is not None:
            self.overlay.destroy()
            self.overlay = None

    # ------------------------------------------------------------ ranglista
    def show_scores(self, category):
        """Felugró ablakban megmutatja az adott kategória top 5 eredményét."""
        window = tk.Toplevel(self.root)
        window.title("Ranglista")
        window.configure(bg=cfg.BG, padx=40, pady=26)
        window.resizable(False, False)

        mode, _, level = category.partition("_")
        mode_name = "Kártyapár-kereső" if mode == "memory" else "Színsorozat"
        tk.Label(window, text="Ranglista", bg=cfg.BG, fg=cfg.TEXT,
                 font=(cfg.FONT_FAMILY, 22, "bold")).pack()
        tk.Label(window, text=f"{mode_name} – {level}", bg=cfg.BG, fg=cfg.ACCENT_HI,
                 font=(cfg.FONT_FAMILY, 12)).pack(pady=(0, 14))

        top = self.score_manager.get_top(category)
        if not top:
            tk.Label(window, text="Még nincs eredmény ezen a szinten.", bg=cfg.BG,
                     fg=cfg.MUTED, font=(cfg.FONT_FAMILY, 12)).pack(pady=10)
        medals = [cfg.GOLD, "#c9d1e3", "#d08c5b"]       # arany, ezüst, bronz
        for rank, entry in enumerate(top, start=1):
            if "level" in entry:
                text = f"{entry['level']}. szint  ·  {get_rank(entry['level'])}"
            else:
                text = f"{entry.get('moves', '?')} lépés · {format_time(entry.get('seconds', 0))}"
            color = medals[rank - 1] if rank <= 3 else cfg.TEXT
            tk.Label(window, text=f"{rank}.   {text}", bg=cfg.PANEL, fg=color, anchor="w",
                     width=28, padx=14, pady=8,
                     font=(cfg.FONT_FAMILY, 13, "bold")).pack(pady=3)

        styled_button(window, "Bezárás", window.destroy).pack(pady=(18, 0))
        window.bind("<Escape>", lambda event: window.destroy())

    # ------------------------------------------------------------ visszalépés
    def back_to_menu(self):
        """Leállítja a játékot, bezárja a keretét, és visszalép a főmenübe."""
        self.stop()
        self.frame.destroy()
        self.on_exit()
