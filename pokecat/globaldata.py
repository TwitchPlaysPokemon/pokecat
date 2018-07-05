
from functools import partial
from os import path

from .datautils import load_from_json_list, get_exact, find_similar


ROOT_DIR = path.dirname(path.abspath(__file__))

NATURES = load_from_json_list(path.join(ROOT_DIR, "globaldata/natures.json"))
TYPES = load_from_json_list(path.join(ROOT_DIR, "globaldata/types.json"))

DEOXYS_BASESTATS = load_from_json_list(path.join(ROOT_DIR, "globaldata/deoxys_basestats.json"))
WORMADAM_BASESTATS = load_from_json_list(path.join(ROOT_DIR, "globaldata/wormadam_basestats.json"))
NATURAL_GIFT_EFFECTS = load_from_json_list(path.join(ROOT_DIR, "globaldata/natural_gift_effects.json"))

get_nature = partial(get_exact, NATURES)
find_nature = partial(find_similar, NATURES)
