import re
from contextlib import suppress

from .objects import (Species, Stats, Nature, Item,
                      Ability, Pokemon, Move)


def get_gender_number(gender):
    if gender == "m":
        return 0
    if gender == "f":
        return 1
    if gender is None or gender == "-":
        return 2
    raise ValueError("Gender must be either m, f or None. - is also acceptable, but discouraged") 

TYPES = [
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy",
]

def get_type_number(type_):
    if type_ in TYPES:
        return TYPES.index(type_)
    return -1


def get_category_number(category):
    if category == "Phsyical":
        return 0
    if category == "Special":
        return 1
    if category == "Status":
        return 2
    raise ValueError("Category must be Physical, Special or Status")


def construct_stats_from_dict(stats):
    stats["def_"] = stats["def"]
    del stats["def"]
    return Stats(**stats)


def construct_pokemon_from_dict(data):
    map_ = {
        "ivs": Stats,
        "evs": Stats,
        "stats": Stats,
        "nature": Nature,
        "item": Item,
        "ball": Item,
        "ability": Ability,
    }
    for key, object_class in map_.items():
        thing = data.get(key)
        if thing:
            if object_class == Stats:
                data[key] = construct_stats_from_dict(thing)
            else:
                data[key] = object_class(**thing)
    species = data["species"]
    if species:
        species["basestats"] = construct_stats_from_dict(species["basestats"])
        species["types"] = tuple(species["types"])
        data["species"] = Species(**species)
    moves = data["moves"]
    for i, move in enumerate(moves):
        if not move:
            continue
        with suppress(KeyError):
            del move["name_id"]
        moves[i] = Move(**move)
    data["moves"] = tuple(moves)
    return Pokemon(**data)


POKEMON_NAME_NORMALIZATIONS = {
    "nidoran♂": "nidoran-m",
    "nidoran♀": "nidoran-f",
    "nidoranm": "nidoran-m",
    "nidoranf": "nidoran-f",
    "nidoran(m)": "nidoran-m",
    "nidoran(f)": "nidoran-f",
    "nidoran\x0b": "nidoran-m",
    "nidoran\x0c": "nidoran-f",
    "farfetch'd": "farfetchd",
    "flab\u00e9b\u00e9": "flabebe",
    "mr. mime": "mr-mime",
    "mr.mime": "mr-mime",
    "mrmime": "mr-mime",
    "mime jr.": "mime-jr",
    "mime-jr.": "mime-jr",
    "mimejr": "mime-jr",
    "mimejr.": "mime-jr",
    "type:null": "type-null",
    "type: null": "type-null",
    "type:-null": "type-null",
    "typenull": "type-null",
    "tapukoko": "tapu-koko",
    "tapu koko": "tapu-koko",
    "tapulele": "tapu-lele",
    "tapu lele": "tapu-lele",
    "tapubulu": "tapu-bulu",
    "tapu bulu": "tapu-bulu",
    "tapufini": "tapu-fini",
    "tapu fini": "tapu-fini",
    "hooh": "ho-oh",
}
def normalize_name(name):
    """Normalizes Pokemon names to be stripped, lowercase and ascii-compatible,
    and also collapses variations of names into one common one.
    E.g. turns Nidoran♂ into nidoran-m"""
    name = name.lower()
    for search, replace in POKEMON_NAME_NORMALIZATIONS.items():
        name = name.replace(search, replace)
    name = name.strip()
    name = name.replace(" ", "-")
    name = re.sub("[^a-z0-9-]+", "", name)
    return name
