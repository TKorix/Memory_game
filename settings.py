"""settings.py - a program közös beállításai és konstansai.

Minden szín, méret, időzítés és szöveges lista itt van egy helyen,
így a többi fájlban nincsenek "szétszórt" számok és színkódok.
"""

# ---------------------------------------------------------------- Általános
APP_NAME = "Mnemo"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
SCORE_FILE = "scores.json"   # a ranglista fájlja (futás közben jön létre)
MAX_SCORES = 5               # hány eredményt őrzünk kategóriánként
SOUND_ENABLED = True         # induláskor be van-e kapcsolva a hang

# ---------------------------------------------------------------- Megjelenés
BG = "#12141c"               # a program háttere
PANEL = "#1c2030"            # panelek, gombok háttere
PANEL_HI = "#262c44"         # kiemelt panel / gomb
BUTTON_HOVER = "#343c5e"     # gomb, ha fölé visszük az egeret
ACCENT = "#6c7cff"           # fő kiemelő szín
ACCENT_HI = "#8794ff"        # világosabb kiemelő szín
TEXT = "#e8eaf6"             # fő szövegszín
MUTED = "#8a90ad"            # halványabb szöveg
SUCCESS = "#2ecc71"          # siker (zöld)
DANGER = "#ff5c6c"           # hiba (piros)

FONT_FAMILY = "Segoe UI"
SYMBOL_FONT = "Segoe UI Symbol"

# ---------------------------------------------------- Kártyapár-kereső mód
# nehézségi szint -> (sorok száma, oszlopok száma)
DIFFICULTIES = {
    "Könnyű": (3, 4),    # 12 kártya, 6 pár
    "Közepes": (4, 4),   # 16 kártya, 8 pár
    "Nehéz": (4, 6),     # 24 kártya, 12 pár
}
# nehézségi szint -> egy kártya mérete pixelben
CARD_SIZES = {"Könnyű": 112, "Közepes": 96, "Nehéz": 84}

# A kártyákon megjelenő szimbólumok (12 darab, a Nehéz szinthez ennyi kell)
SYMBOLS = ["★", "♥", "♦", "♣", "♠", "♪", "☀", "☾", "☂", "✿", "☺", "⚑"]
# Minden szimbólumnak saját színe van (a SYMBOLS sorrendjében)
SYMBOL_COLORS = [
    "#ff9f43", "#ff5c6c", "#ee5253", "#10ac84", "#5f27cd", "#2e86de",
    "#feca57", "#54a0ff", "#48dbfb", "#ff6bcb", "#1dd1a1", "#a55eea",
]

CARD_BACK = "#2b3150"        # lefordított kártya színe
CARD_BACK_HI = "#3b4372"     # lefordított kártya, ha fölötte az egér
CARD_BORDER = "#3a4170"
CARD_PATTERN = "#4a5390"     # a kártyahát mintája
CARD_FACE = "#f4f5fb"        # felfordított kártya színe
CARD_MATCHED = "#e3f8ec"     # megtalált pár színe
SHADOW = "#0a0b10"

FLIP_STEPS = 8               # a kártyafordítás animációjának lépései
FLIP_STEP_MS = 16            # egy animációs lépés ideje (ms)
MISMATCH_DELAY = 900         # ennyi ideig látszik a rossz páros (ms)

# --------------------------------------------------- Színsorozat (Simon) mód
SIMON_SIZE = 170             # egy színes gomb mérete pixelben
# (alapszín, felvillanó szín) - a gombok sorrendje: zöld, piros, sárga, kék
SIMON_COLORS = [
    ("#1e9e55", "#6dffa6"),
    ("#b8323f", "#ff8794"),
    ("#c9a227", "#fff27d"),
    ("#2a63c9", "#8dbaff"),
]
SIMON_TONES = [392, 330, 262, 494]   # a gombokhoz tartozó hangok (Hz)

# sebesség -> (felvillanás ideje ms, szünet két felvillanás között ms)
SIMON_SPEEDS = {
    "Lassú": (650, 280),
    "Normál": (480, 200),
    "Gyors": (320, 140),
}
SIMON_SPEEDUP = 8            # minden körben ennyi ms-mal gyorsul a lejátszás
SIMON_MIN_FLASH = 150        # ennél gyorsabb nem lesz a felvillanás
SIMON_MIN_GAP = 70           # ennél kisebb nem lesz a szünet
SIMON_START_DELAY = 700      # a sorozat lejátszása előtti várakozás (ms)
