
from os import path
from functools import partial
from .utils import normalize_name
from .datautils import build_from_json_list, load_from_json_list, get_exact, find_similar

from .globaldata import *  # forward


ROOT_DIR = path.dirname(path.abspath(__file__))

ABILITIES = list(build_from_json_list(path.join(ROOT_DIR, "gen4data/abilities.json")))
ITEMS     = list(build_from_json_list(path.join(ROOT_DIR, "gen4data/items.json")))
MOVES     = load_from_json_list(path.join(ROOT_DIR, "gen4data/moves.json"))
# remove moves without ids
MOVES     = [m for m in MOVES if m["id"] is not None]
BALLS     = load_from_json_list(path.join(ROOT_DIR, "pbrdata/balls.json"))
POKEDEX   = load_from_json_list(path.join(ROOT_DIR, "gen4data/pokedex.json"))

get_ability = partial(get_exact, ABILITIES)
get_item    = partial(get_exact, ITEMS)
get_move    = partial(get_exact, MOVES)
get_pokemon = partial(get_exact, POKEDEX)
_ball_namegetter = lambda b: b["name"].rsplit(" Ball", 1)[0]
get_ball    = partial(get_exact, BALLS, namegetter=_ball_namegetter)

find_ability = partial(find_similar, ABILITIES)
find_item    = partial(find_similar, ITEMS)
find_move    = partial(find_similar, MOVES)
def find_pokemon(name):
    return find_similar(POKEDEX, normalize_name(name), namegetter=lambda n: normalize_name(n["name"]))
find_ball    = partial(find_similar, BALLS, namegetter=_ball_namegetter)
