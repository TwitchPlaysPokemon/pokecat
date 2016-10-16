
import re
from enum import IntEnum
from collections import namedtuple


Species = namedtuple("Species", ["id", "name", "basestats", "types"])
Ability = namedtuple("Ability", ["id", "name", "description"])
Ability.__new__.__defaults__ = ("",)
Item    = namedtuple("Item",    ["id", "name", "description"])
Item.__new__.__defaults__ = ("",)
Nature  = namedtuple("Nature",  ["id", "name", "increased", "decreased", "descriptions"])
Nature.__new__.__defaults__ = ("",)

Species = namedtuple("Species", ["id", "name", "basestats", "types"])
def species_asdict(species):
    return {
        "id": species.id,
        "name": species.name,
        "basestats": species.basestats._asdict(),
        "types": species.types,
    }
Species._asdict = species_asdict

Stats = namedtuple("Stats", ["hp", "atk", "def_", "spA", "spD", "spe"])
def stats_asdict(stats):
    return {
        "hp": stats.hp,
        "atk": stats.atk,
        "def": stats.def_,
        "spA": stats.spA,
        "spD": stats.spD,
        "spe": stats.spe,
    }
Stats._asdict = stats_asdict

Move = namedtuple("Move", ["id", "category", "type", "accuracy", "name", "displayname", "power", "pp", "pp_ups"])
Move.name_id = property(lambda self: re.sub(r"[^a-zA-Z0-9]", "", self.name).lower())
Move.__new__.__defaults__ = (0,)

class Type(IntEnum):
    Normal   = 0
    Fire     = 1
    Water    = 2
    Electric = 3
    Grass    = 4
    Ice      = 5
    Fighting = 6
    Poison   = 7
    Ground   = 8
    Flying   = 9
    Psychic  = 10
    Bug      = 11
    Rock     = 12
    Ghost    = 13
    Dragon   = 14
    Dark     = 15
    Steel    = 16
    Fairy    = 17
    Unknown  = 18

class Category(IntEnum):
    Physical = 0
    Special  = 1
    Status   = 2

Pokemon = namedtuple("Pokemon", ["species", "moves", "ivs", "evs", "gender", "level", "nature", "stats", "rarity", "setname", "biddable", "displayname", "ingamename", "item", "ability", "form", "shiny", "happiness", "ball"])
Pokemon.__new__.__defaults__ = (0.0, "", False, "", "", None, None, None, 0, False, 0, None)
def pokemon_asdict(pokemon):
    return {
        "species": pokemon.species._asdict(),
        "moves": [move._asdict() for move in pokemon.moves],
        "ivs": pokemon.ivs._asdict(),
        "evs": pokemon.evs._asdict(),
        "gender": pokemon.gender,
        "level": pokemon.level,
        "nature": pokemon.nature._asdict(),
        "stats": pokemon.stats._asdict() if pokemon.stats else None,
        "rarity": pokemon.rarity,
        "setname": pokemon.setname,
        "biddable": pokemon.biddable,
        "displayname": pokemon.displayname,
        "ingamename": pokemon.ingamename,
        "item": pokemon.item._asdict() if pokemon.item else None,
        "ability": pokemon.ability._asdict() if pokemon.ability else None,
        "form": pokemon.form,
        "shiny": pokemon.shiny,
        "happiness": pokemon.happiness,
        "ball": pokemon.ball._asdict() if pokemon.ball else None,
    }
Pokemon._asdict = pokemon_asdict
Pokemon.id = property(lambda self: (self.species.id, self.setname))
