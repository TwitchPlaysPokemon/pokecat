
from .gen4data import NATURES

# the default order for most things.
statnames = ("hp", "atk", "def", "spA", "spD", "spe")
# some internal representations have speed stuck inbetween.
statnames_internal = ("hp", "atk", "def", "spe", "spA", "spD")


def calculate_stat(base, ev, iv, stattype, nature, level=100):
    """
    Calculated the actual stat of a Pokémon.
    Arguments:
        base: basestat for that Pokémon
        ev: ev for that stat the Pokémon has
        iv: iv for that stat the Pokémon has
        stattype: type of the stat being calculated.
            can be hp, atk, def, spA, spD and spe
        nature: nature dict of the Pokémon's nature.
        level: default 100. level of the Pokémon
    """
    stattype = stattype.lower()
    is_hp = stattype == "hp"
    growth = base*2 + (ev // 4) + iv + (100 if is_hp else 0)
    stat = (10 if is_hp else 5) + (growth * level) // 100
    nature_val = 10
    if nature["increased"] and nature["decreased"]:
        if nature["increased"].lower() == stattype:
            nature_val = 11
        elif nature["decreased"].lower() == stattype:
            nature_val = 9
    return (stat * nature_val) // 10
