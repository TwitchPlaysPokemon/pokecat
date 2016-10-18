
import json
from os import path
from operator import itemgetter
from functools import partial
from Levenshtein import ratio #@UnresolvedImport
from .utils import normalize_name

ROOT_DIR = path.dirname(path.abspath(__file__))

def _build_from_json_list(filename):
    with open(path.join(ROOT_DIR, filename), "r", encoding="utf-8") as f:
        list_ = json.load(f)
    for i, item in enumerate(list_):
        yield {
            "id": i,
            "name": item,
            "description": "",
        }

def _load_from_json_list(filename):
    with open(path.join(ROOT_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)

ABILITIES = list(_build_from_json_list("gen4data/abilities.json"))
ITEMS     = list(_build_from_json_list("gen4data/items.json"))
MOVES     = _load_from_json_list("gen4data/moves.json")
# remove moves without ids
MOVES     = [m for m in MOVES if m["id"] is not None]
BALLS     = _load_from_json_list("pbrdata/balls.json")
POKEDEX   = _load_from_json_list("gen4data/pokedex.json")

NATURES   = _load_from_json_list("globaldata/natures.json")
TYPES     = _load_from_json_list("globaldata/types.json")

DEOXYS_BASESTATS     = _load_from_json_list("globaldata/deoxys_basestats.json")
NATURAL_GIFT_EFFECTS = _load_from_json_list("globaldata/natural_gift_effects.json")


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

_ball_namegetter = lambda b: b["name"].rsplit(" Ball", 1)[0]
get_ability = partial(_get_exact, ABILITIES, namegetter=itemgetter("name"))
get_item    = partial(_get_exact, ITEMS,     namegetter=itemgetter("name"))
get_move    = partial(_get_exact, MOVES,     namegetter=itemgetter("name"))
get_nature  = partial(_get_exact, NATURES,   namegetter=itemgetter("name"))
get_pokemon = partial(_get_exact, POKEDEX,   namegetter=itemgetter("name"))
get_ball    = partial(_get_exact, BALLS,     namegetter=_ball_namegetter)

def _find_similar(lst, name, min_similarity=0.75, namegetter=lambda x:x, idgetter=None):
    '''
    Finds something by name, which doesn't have to be an exact match.
    Returns a dict {id: item} which items that satisfy the needed similarity.

    If the dict is empty, no items matched. If it has more than 1 item,
    the supplied item's name should be considered ambiguous.
    '''
    entries = {}
    highest_similarity = 0
    for index, item in enumerate(lst):
        if not item or not item["name"]:
            continue  # null item, for lists having nothing as id 0 for example
        actual_name = namegetter(item)
        if idgetter:
            id_ = idgetter(item)
        else:
            id_ = index
        similarity = ratio(name.lower(), actual_name.lower())
        if similarity == 1.0:
            # full match, just return this
            return {id_:item}
        if similarity - highest_similarity > 0.1:
            # the rest isn't close enough, ditch them
            entries.clear()
        if similarity >= min_similarity and highest_similarity - similarity < 0.1:
            entries[id_] = item
        highest_similarity = max(highest_similarity, similarity)
    return entries

find_ability = partial(_find_similar, ABILITIES, namegetter=itemgetter("name"), idgetter=itemgetter("id"))
find_item    = partial(_find_similar, ITEMS,     namegetter=itemgetter("name"), idgetter=itemgetter("id"))
find_move    = partial(_find_similar, MOVES,     namegetter=itemgetter("name"), idgetter=itemgetter("id"))
find_nature  = partial(_find_similar, NATURES,   namegetter=itemgetter("name"))
def find_pokemon(name):
    return _find_similar(POKEDEX, normalize_name(name), namegetter=lambda n: normalize_name(n["name"]), idgetter=itemgetter("id"))
find_ball    = partial(_find_similar, BALLS,     namegetter=_ball_namegetter,   idgetter=itemgetter("id"))
