

from .objects import (Species, Stats, Nature, Item,
                      Ability, Pokemon, Move, Type)

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


def construct_pokemon_from_dict(data):
    map_ = {
        "ivs": Stats,
        "evs": Stats,
        "nature": Nature,
        "item": Item,
        "ability": Ability,
    }
    for key, object_class in map_.items():
        thing = data.get(key)
        if thing:
            data[key] = object_class(**thing)
    species = data["species"]
    if species:
        species["basestats"] = Stats(**species["basestats"])
        data["species"] = Species(**species["basestats"])
    moves = data["moves"]
    for i, move in enumerate(moves):
        if not move:
            continue
        moves[i] = Move(**move)
    return Pokemon(**data)

