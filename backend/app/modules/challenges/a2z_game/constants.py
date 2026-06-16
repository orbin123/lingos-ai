"""Constants for the A2Z Challenge game."""

A2Z_SLUG = "a2z"

# 24 playable letters — Q and X are excluded (too few common words).
A2Z_LETTERS: list[str] = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "Y",
    "Z",
]

TOTAL_LETTERS: int = len(A2Z_LETTERS)  # 24

MAX_LEVEL: int = 3

# Default level configurations (source of truth is DB via seed script;
# these exist only as documentation / fallback reference).
DEFAULT_LEVELS = (
    {
        "level_number": 1,
        "name": "Warm-up",
        "target_words": 10,
        "round_time_seconds": 25,
    },
    {"level_number": 2, "name": "Stride", "target_words": 15, "round_time_seconds": 32},
    {
        "level_number": 3,
        "name": "Fluency",
        "target_words": 22,
        "round_time_seconds": 45,
    },
)
