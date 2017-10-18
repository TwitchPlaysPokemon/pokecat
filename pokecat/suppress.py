from enum import Enum


class Suppressions(Enum):
    INVALID_EVS     = "invalid-evs"
    WASTED_EVS      = "wasted-evs"
    DUPLICATE_MOVES = "duplicate-moves"
    PUBLIC_SHINY    = "public-shiny"
