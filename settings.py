"""A játék közös beállításai."""

APP_NAME = "Memória"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
SCORE_FILE = "scores.json"

BG = "#101827"
PANEL = "#19263b"
CARD_BACK = "#263a59"
CARD_FRONT = "#f4f7ff"
TEXT = "#f4f7ff"
MUTED = "#a9b8d0"
ACCENT = "#67e8c1"
GOOD = "#36b995"
BAD = "#f07878"
BUTTON = "#2c4262"
BUTTON_HOVER = "#3b567c"

FONT = "Segoe UI"
TITLE_FONT = (FONT, 30, "bold")
BODY_FONT = (FONT, 12)
BUTTON_FONT = (FONT, 14, "bold")
CARD_FONT = (FONT, 24, "bold")

DIFFICULTIES = {
    "Könnyű": (3, 4),
    "Közepes": (4, 4),
    "Nehéz": (4, 6),
}

SYMBOLS = [
    "🍓", "🍋", "🐱", "🐸", "🌟", "🚀",
    "🍀", "🎈", "🐼", "⚽", "🌈", "🎵",
]

SIMON_COLORS = ["#ff627d", "#43d9a3", "#5a9cff", "#ffc857"]
SIMON_LIGHT_COLORS = ["#ff9aaa", "#8af0c6", "#9ac4ff", "#ffe29a"]
SIMON_SPEEDS = {
    "Lassú": 850,
    "Normál": 600,
    "Gyors": 400,
}

MISMATCH_DELAY = 850
SIMON_FLASH_DELAY = 220
