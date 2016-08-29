
import json
from os import path
from operator import itemgetter
from functools import partial
from Levenshtein import ratio


ROOT_DIR = path.dirname(path.abspath(__file__))

ABILITIES = json.load(open(path.join(ROOT_DIR, "gen4data", "abilities.json"), encoding="utf-8"))
ITEMS     = json.load(open(path.join(ROOT_DIR, "gen4data", "items.json"),     encoding="utf-8"))
MOVES     = json.load(open(path.join(ROOT_DIR, "gen4data", "moves.json"),     encoding="utf-8"))
POKEDEX   = json.load(open(path.join(ROOT_DIR, "gen4data", "pokedex.json"),   encoding="utf-8"))

NATURES   = json.load(open(path.join(ROOT_DIR, "globaldata", "natures.json"), encoding="utf-8"))
TYPES     = json.load(open(path.join(ROOT_DIR, "globaldata", "types.json"),   encoding="utf-8"))

DEOXYS_BASESTATS     = json.load(open(path.join(ROOT_DIR, "globaldata", "deoxys_basestats.json"), encoding="utf-8"))
NATURAL_GIFT_EFFECTS = json.load(open(path.join(ROOT_DIR, "globaldata", "natural_gift_effects.json"), encoding="utf-8"))


def _get_exact(lst, name, namegetter=lambda x:x):
    '''
    Gets something by name, which has to match exactly.
    Either returns the matching item, or None if none was found.
    '''
    for item in lst:
        if not item:
            continue  # null item, for lists having nothing as id 0 for example
        if name == namegetter(item):
            return item
    return None

get_ability = partial(_get_exact, ABILITIES)
get_item    = partial(_get_exact, ITEMS)
get_move    = partial(_get_exact, MOVES,   namegetter=itemgetter("name"))
get_nature  = partial(_get_exact, NATURES, namegetter=itemgetter("name"))
get_pokemon = partial(_get_exact, POKEDEX, namegetter=itemgetter("name"))
def get_ball(ballname):
    for item in ITEMS:
        if not item:
            continue
        if item.endswith(" Ball") and item[:-5] == ballname:
            return item
    return None

def _find_similar(lst, name, min_similarity=0.75, namegetter=lambda x:x, idgetter=None):
    '''
    Finds something by name, which doesn't have to be an exact match.
    Returns a dict {id: item} which items that satisfy the needed similarity.

    If the dict is empty, no items matched. If it has more than 1 item,
    the supplied item's name should be considered ambiguous.
    '''
    entries = {}
    for index, item in enumerate(lst):
        if not item:
            continue  # null item, for lists having nothing as id 0 for example
        actual_name = namegetter(item)
        if idgetter:
            id_ = idgetter(item)
        else:
            id_ = index
        similarity = ratio(name, actual_name)
        if similarity >= min_similarity:
            entries[id_] = item
    return entries

find_ability = partial(_find_similar, ABILITIES)
find_item    = partial(_find_similar, ITEMS)
find_move    = partial(_find_similar, MOVES,   namegetter=itemgetter("name"), idgetter=itemgetter("id"))
find_nature  = partial(_find_similar, NATURES, namegetter=itemgetter("name"))
find_pokemon = partial(_find_similar, POKEDEX, namegetter=itemgetter("name"), idgetter=itemgetter("id"))
def find_ball(ballname, min_similarity=0.75):
    balls = {}
    for index, item in enumerate(ITEMS):
        if not item:
            continue
        if item.endswith(" Ball") and ratio(item[:-5], ballname) >= min_similarity:
            balls[index] = item
    return balls
