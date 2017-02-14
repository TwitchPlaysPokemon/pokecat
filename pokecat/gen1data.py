
from os import path
from functools import partial
from .datautils import build_from_json_dict, get_exact, find_similar

from .globaldata import *  # forward


ROOT_DIR = path.dirname(path.abspath(__file__))

ITEMS = list(build_from_json_dict(path.join(ROOT_DIR, "gen1data/items.json")))
# TODO MOVES
# TODO POKEDEX

get_item  = partial(get_exact, ITEMS)
find_item = partial(find_similar, ITEMS)
