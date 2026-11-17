"""settings.py - a program közös beállításai.

Minden szín, méret és szám itt van egy helyen, a többi fájl innen olvassa ki.
Ha valamit át akarunk állítani (pl. a színeket), elég itt módosítani.
"""

# ------------------------------------------------------------ Általános
APP_NAME = "Mnemo"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
SCORE_FILE = "scores.json"    # ide mentjük a ranglistát (futás közben jön létre)
MAX_SCORES = 5                # ennyi eredményt őrzünk kategóriánként

SOUND_ENABLED = True          # induláskor szóljon-e a hang
SOUND_VOLUME = 0.6            # hangerő (0 és 1 között)
SAMPLE_RATE = 22050           # a hangok minősége

# ------------------------------------------------------------ Színek és betűk
BG = "#0f111a"                # a program háttere
BOARD_BG = "#171a28"          # a játéktér háttere
BOARD_BORDER = "#2a3050"      # a játéktér kerete
PANEL = "#1c2030"             # panelek háttere
PANEL_HI = "#262c44"          # gombok háttere
BUTTON_HOVER = "#343c5e"      # gomb, ha fölötte az egér
ACCENT = "#6c7cff"            # fő kiemelő szín
ACCENT_HI = "#8794ff"         # világosabb kiemelő szín
TEXT = "#e8eaf6"              # szövegszín
MUTED = "#8a90ad"             # halványabb szöveg
SUCCESS = "#2ecc71"           # zöld (siker)
DANGER = "#ff5c6c"            # piros (hiba)
GOLD = "#ffd166"              # arany (csillagok)
SHADOW = "#0a0b10"            # árnyék

FONT_FAMILY = "Segoe UI"
SYMBOL_FONT = "Segoe UI Symbol"

# ------------------------------------------------------------ Kártyapár-kereső
# nehézségi szint -> (sorok száma, oszlopok száma)
DIFFICULTIES = {
    "Könnyű": (3, 4),     # 12 kártya = 6 pár
    "Közepes": (4, 4),    # 16 kártya = 8 pár
    "Nehéz": (4, 6),      # 24 kártya = 12 pár
}
# nehézségi szint -> egy kártya mérete pixelben
CARD_SIZES = {"Könnyű": 104, "Közepes": 88, "Nehéz": 80}

# A kártyákon lévő szimbólumok (12 darab)
SYMBOLS = ["★", "♥", "♦", "♣", "♠", "♪", "☀", "☾", "☂", "✿", "☺", "⚑"]
# Témák: mi legyen a kártyákon (mindegyikből 12 darab kell)
THEMES = {
    "Jelek": SYMBOLS,
    "Betűk": list("ABCDEFGHIJKL"),
    "Számok": [str(n) for n in range(1, 13)],
}
# A szimbólumok színei (a téma elemeinek sorrendjében)
SYMBOL_COLORS = ["#ff9f43", "#ff5c6c", "#ee5253", "#10ac84", "#5f27cd", "#2e86de",
                 "#feca57", "#54a0ff", "#48dbfb", "#ff6bcb", "#1dd1a1", "#a55eea"]

CARD_BACK = "#2b3150"         # lefordított kártya
CARD_BACK_HI = "#3b4372"      # lefordított kártya, ha fölötte az egér
CARD_BORDER = "#3a4170"
CARD_PATTERN = "#4a5390"      # a kártyahát mintája
CARD_FACE = "#e4e8f6"         # felfordított kártya
CARD_MATCHED = "#dff7e9"      # megtalált pár

HINTS_PER_GAME = 2            # ennyi segítség jár egy játékra (mindegyik 2 lépésbe kerül)
MISMATCH_DELAY = 900          # ennyi ideig látszik a rossz páros (ms)
# Játék elején ennyi ideig látszanak a kártyák, hogy meg lehessen jegyezni őket (ms)
PREVIEW_MS = {"Könnyű": 2200, "Közepes": 2000, "Nehéz": 2600}
# Csillagok -> cím a játék végén
MEMORY_RANKS = {3: "Memóriamester", 2: "Ügyes játékos", 1: "Gyakorolj még!"}

# ------------------------------------------------------------ Színsorozat (Simon)
SIMON_SIZE = 160              # egy színes gomb mérete pixelben
# (alapszín, felvillanó szín) - sorrend: zöld, piros, sárga, kék
SIMON_COLORS = [("#1e9e55", "#6dffa6"), ("#b8323f", "#ff8794"),
                ("#c9a227", "#fff27d"), ("#2a63c9", "#8dbaff")]
SIMON_TONES = [392, 330, 262, 494]    # a gombok hangjai (Hz)

# sebesség -> (felvillanás ideje ms, szünet két felvillanás között ms)
SIMON_SPEEDS = {"Lassú": (650, 280), "Normál": (480, 200), "Gyors": (320, 140)}
SIMON_SPEEDUP = 8             # minden körben ennyi ms-mal gyorsabb a lejátszás
SIMON_MIN_FLASH = 120         # ennél gyorsabb nem lesz
# Simon rangok: (ennyi szinttől, cím)
RANKS = [(0, "Újonc"), (4, "Tanuló"), (8, "Haladó"), (12, "Profi"), (16, "Mester"), (20, "Legenda")]

# Tippek a főmenüben (véletlenszerűen jelenik meg egy)
TIPS = ["Tipp: a kártyák helyét a játék elején jegyezd meg!",
        "Tipp: a Simonban segít, ha ritmusban mondod magadban a sorozatot.",
        "Tipp: a kombó (több találat egymás után) egyre magasabb hangot ad.",
        "Tipp: az 1-4 billentyűkkel is játszhatsz a Simonban.",
        "Tipp: a szóköz bármikor új játékot indít."]
