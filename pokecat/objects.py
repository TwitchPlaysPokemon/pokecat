
import re
from enum import IntEnum
from collections import namedtuple

from .stats import calculate_stat, statnames


Species = namedtuple("Species", ["id", "name", "basestats", "types"])
Ability = namedtuple("Ability", ["id", "name", "description"])
Item    = namedtuple("Item",    ["id", "name", "description"])
Nature  = namedtuple("Nature",  ["id", "name", "descriptions", "increased", "decreased"])


class Species:
    def __init__(self, id, name, basestats, types):
        self.id = id,
        self.name = name,
        self.basestats = basestats
        self.types = types

    def asdict(self):
        return {
            "id": self.id,
            "name": self.name,
            "basestats": self.basestats.asdict(),
            "types": self.types,
        }


class Stats:
    def __init__(self, hp=0, atk=0, def_=0, spA=0, spD=0, spe=0):
        self.hp = hp
        self.atk = atk
        self.def_ = def_
        self.spA = spA
        self.spD = spD
        self.spe = spe

    def calculate(self, ev, iv, stattype, nature, level=100):
        stats_calculated = {}
        for statname in statnames:
            base = getattr(self, statname)
            val = calculate_stat(base, ev, iv, stattype, nature, level)
            stats_calculated[statname] = val
        return Stats(**stats_calculated)
    
    def asdict(self):
        dict_ = {}
        for statname in statnames:
            dict_[statname] = getattr(self, statname)
        return dict_


class Move:
    def __init__(self, id, category, type, accuracy, name, power, pp, pp_ups=0, name_id=None):
        self.id = id
        self.category = category
        self.type = type
        self.accuracy = accuracy
        self.name = name
        self.power = power
        self.pp = pp
        self.pp_ups = pp_ups
        self.name_id = name_id or re.sub(r"[ _-]", "", name)

    def asdict(self):
        return {
            "id": self.id,
            "category": self.category,
            "type": self.type,
            "accuracy": self.accuracy,
            "name": self.name,
            "power": self.power,
            "pp": self.pp,
            "pp_ups": self.pp_ups,
            "name_id": self.name_id,
        }


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


class Pokemon:
    def __init__(self, species, moves, ivs, evs, gender, level, nature,
                 item=None, ability=None, form=0, shiny=False, happiness=0,
                 **kwargs):
        # obligatory
        self.species = species
        self.moves   = moves
        self.ivs     = ivs
        self.evs     = evs
        self.gender  = gender
        self.level   = level
        self.nature  = nature
        # optional
        self.item    = item
        self.ability = ability
        self.form    = form
        self.shiny   = shiny
        self.happiness = happiness
        # extra data
        self.extra   = kwargs

    def asdict(self):
        return {
            "species": self.species.asdict(),
            "moves": [move.asdict() for move in self.moves],
            "ivs": self.ivs.asdict(),
            "evs": self.evs.asdict(),
            "gender": self.gender,
            "level": self.level,
            "nature": self.nature,
            "item": self.item._asdict(),
            "ability": self.ability._asdict(),
            "form": self.form,
            "shiny": self.shiny,
            "happiness": self.happiness,
            "extra": self.extra,
        }

