
from os import path
from functools import partial
from .datautils import load_from_json_list, build_from_json_dict, get_exact, find_similar

from .globaldata import *  # forward


ROOT_DIR = path.dirname(path.abspath(__file__))

ITEMS = list(build_from_json_dict(path.join(ROOT_DIR, "gen1data/items.json")))
MOVES = load_from_json_list(path.join(ROOT_DIR, "gen1data/moves.json"))
# TODO POKEDEX

get_item = partial(get_exact, ITEMS)
get_move = partial(get_exact, MOVES)

find_item = partial(find_similar, ITEMS)
find_move = partial(find_similar, MOVES)
