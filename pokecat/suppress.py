from enum import Enum


class Suppressions(Enum):
    INVALID_EV      = "invalid-ev"
    WASTED_EV       = "wasted-ev"
    DUPLICATE_MOVES = "duplicate-moves"
    PUBLIC_SHINY    = "public-shiny"
