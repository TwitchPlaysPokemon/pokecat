
import re
import sys
from copy import deepcopy
from functools import partial
import random
import logging
from warnings import warn

from . import gen4data, forms, stats

log = logging.getLogger(__name__)

_OBLIGATORY_FIELDS = {"ingamename", "setname", "species", "ability", "nature", "ivs", "evs", "moves"}
_OPTIONAL_FIELDS = {"gender": None, "form": 0, "item": None, "displayname": None, "happiness": 255, "shiny": False,
                    "biddable": None, "rarity": 1.0, "ball": "Poké", "level": 100, "combinations": [], "separations": []}


# just code recycling for populate_pokeset()
def _get_by_index_or_name(lst, index_or_name, name_of_thing, get_func, find_func):
    if index_or_name is None:
        return None, True
    if isinstance(index_or_name, int):
        try:
            thing = lst[index_or_name]
        except IndexError:
            raise ValueError("Invalid %s number: %d" % (name_of_thing, index_or_name))
    else:
        thing = get_func(index_or_name)
        if not thing:
            candidates = find_func(index_or_name)
            if not candidates or len(candidates) > 1:
                raise ValueError("Unrecognized %s: %s" % (name_of_thing, index_or_name))
            thing = next(iter(candidates.values()))
            return thing, False
    return thing, True


def populate_pokeset(pokeset):
    '''
    Reads in data for one pokeset and populates it with all additionally available
    data. This includes types of Pokémon or per-move data like PP, power or types.

    Arguments:
        set: base data of the set to populate. see the format specification for details.
    Throws:
        ValueError: If the data is not fully parsable. the ValueError's description contains
        further details on the error that occured.
    Returns:
        The populated set. The passed data is not modified
    '''
    # I am sorry that this function is so big and partly copy-pasted,
    # but it just does a lot of equally boring things like processing
    # special cases. I couldn't come up with a structure that wouldn't
    # just feel forced. It could be better, but it could also be worse,
    # and to be honest it's easy enough to maintain (for me at least).
    
    # make deepcopy to not modify original data
    pokeset = deepcopy(pokeset)
    
    # check if there are wrongly capitalized keys
    for key, value in list(pokeset.items()):
        key_lower = key.lower()
        if key_lower != key:
            warn("Key should be all lowercase: %s" % key)
            del pokeset[key]
            pokeset[key_lower] = value

    # check that all obligatory fields are present
    present_fields = set(pokeset.keys())
    missing_fields = _OBLIGATORY_FIELDS - present_fields
    if missing_fields:
        raise ValueError("pokeset is missing obligatory fields: %s" % ", ".join(missing_fields))

    # check if there are unknown fields
    unrecognized_fields = present_fields - (set(_OPTIONAL_FIELDS.keys()) | _OBLIGATORY_FIELDS)
    if unrecognized_fields:
        raise ValueError("pokeset has unrecognized fields: %s" % ", ".join(unrecognized_fields))

    # trim all leading and trailing whitespaces
    # TODO test if the yaml parser already does this
    #for k, v in pokeset.items():
    #    pokeset[k] = v.strip()

    # fill in optional fields
    for key, default in _OPTIONAL_FIELDS.items():
        if key not in pokeset:
            pokeset[key] = default

    # check validity of names
    if not 1 <= len(pokeset["ingamename"]) <= 10:
        raise ValueError("ingamename must be between 1 and 10 characters long: %s" % pokeset["ingamename"])
    if not pokeset["setname"] or not isinstance(pokeset["setname"], str):
        raise ValueError("setname must be a non-empty string")
    if pokeset["displayname"] is not None:
        warn("Using custom displaynames is not recommended. Use the setname to describe a pokeset.")
        if not pokeset["displayname"] or not isinstance(pokeset["displayname"], str):
            raise ValueError("displayname, if set, must be a non-empty string")

    # check and populate species
    species_raw = pokeset["species"]
    species, perfect_match = _get_by_index_or_name(gen4data.POKEDEX, species_raw,
                                                   "species", gen4data.get_pokemon, gen4data.find_pokemon)
    if not perfect_match:
        warn("Didn't recognize species %s, but assumed %s." % (species_raw, species["name"]))
    pokeset["species"] = species

    # check and populate ability. is a list
    ability = []
    ability_raw = pokeset["ability"]
    if not isinstance(ability_raw, list):
        ability_raw = [ability_raw]
    for ability_raw_single in ability_raw:
        ability_single, perfect_match = _get_by_index_or_name(gen4data.ABILITIES, ability_raw_single,
                                                              "ability", gen4data.get_ability, gen4data.find_ability)
        if not perfect_match:
            warn("Didn't recognize ability %s, but assumed %s." % (ability_raw_single, ability_single))
        ability.append(ability_single)
    if len(set(ability)) < len(ability):
        raise ValueError("All abilities supplied must be unique: %s" % ", ".join(ability))
    pokeset["ability"] = ability

    # check and populate item. is a list
    item = []
    item_raw = pokeset["item"]
    if not isinstance(item_raw, list):
        item_raw = [item_raw]
    for item_raw_single in item_raw:
        item_single, perfect_match = _get_by_index_or_name(gen4data.ITEMS, item_raw_single,
                                                           "item", gen4data.get_item, gen4data.find_item)
        if not perfect_match:
            warn("Didn't recognize item %s, but assumed %s." % (item_raw_single, item_single))
        item.append(item_single)
    if len(set(item)) < len(item):
        raise ValueError("All items supplied must be unique: %s" % ", ".join(item))
    pokeset["item"] = item

    # check and populate ball. is a list
    # TODO check against ball-list, not item-list.
    ball = []
    ball_raw = pokeset["ball"]
    if not isinstance(ball_raw, list):
        ball_raw = [ball_raw]
    for ball_raw_single in ball_raw:
        ball_single, perfect_match = _get_by_index_or_name(gen4data.ITEMS, ball_raw_single,
                                                           "ball", gen4data.get_ball, gen4data.find_ball)
        if not ball_single.endswith(" Ball"):
            raise ValueError("Invalid ball: %s" % ball_single)
        if not perfect_match:
            warn("Didn't recognize ball %s, but assumed %s." % (ball_raw_single, ball_single))
        ball.append(ball_single)
    if len(set(ball)) < len(ball):
        raise ValueError("All balls supplied must be unique: %s" % ", ".join(ball))
    pokeset["ball"] = ball

    # check gender
    gender = pokeset["gender"]
    if not isinstance(gender, list):
        gender = [gender]
    for gender_single in gender:
        if gender_single not in ("m", "f", None):
            raise ValueError("gender can only be 'm', 'f' or not set (null), but not %s" % (gender_single,))
    if len(gender) > 1 and None in gender:
        raise ValueError("non-gender cannot be mixed with m/f")
    if len(set(gender)) < len(gender):
        raise ValueError("All genders supplied must be unique: %s" % ", ".join(gender))
    pokeset["gender"] = gender

    # check level
    level = pokeset["level"]
    if not (isinstance(level, int) and 1 <= level <= 100):
        raise ValueError("level must be a number between 1 and 100")

    # check and populate nature. might be defined as "+atk -def" or similar
    nature_raw = pokeset["nature"]
    stats_regex = "|".join(stats.statnames)
    match = re.match(r"^\+({0})\s+-((?:\1){0})$".format(stats_regex), nature_raw)
    if match:
        increased = match.group(1)
        decreased = match.group(2)
        matching_nature = [n for n in gen4data.NATURES if n["increased"] == increased and n["decreased"] == decreased]
        if matching_nature:
            nature_raw = matching_nature[0]["name"]
    nature, perfect_match = _get_by_index_or_name(gen4data.NATURES, nature_raw,
                                                  "nature", gen4data.get_nature, gen4data.find_nature)
    if not perfect_match:
        warn("Didn't recognize nature %s, but assumed %s." % (nature_raw, nature["name"]))
    pokeset["nature"] = nature

    # check IVs
    ivs = pokeset["ivs"]
    if isinstance(ivs, int):
        ivs = {name: ivs for name in stats.statnames}
    if set(stats.statnames) != set(ivs.keys()):
        raise ValueError("ivs must contain the following keys: %s" % ", ".join(stats.statnames))
    if not all(0 <= val <= 31 for val in ivs.values()):
        raise ValueError("All IVs must be between 0 and 31.")
    pokeset["ivs"] = ivs
    # check EVs
    evs = pokeset["evs"]
    if isinstance(evs, int):
        evs = {name: evs for name in stats.statnames}
    if set(stats.statnames) != set(evs.keys()):
        raise ValueError("evs must contain the following keys: %s" % ", ".join(stats.statnames))
    if not all (0 <= val <= 252 for val in evs.values()):
        raise ValueError("All EVs must be between 0 and 252.")
    ev_sum = sum(val for val in evs.values())
    if ev_sum > 510:
        raise ValueError("Sum of EV must not be larger than 510, but is %d" % ev_sum)
    for key, value in evs.items():
        if value % 4 != 0:
            warn("EV for %s is %d, which is not a multiple of 4 (wasted points)" % (key, value))
    pokeset["evs"] = evs

    # TODO outsorce singular move procession
    # check and populate moves
    moves = []
    moves_raw = pokeset["moves"]
    if not 1 <= len(moves_raw) <= 4:
        raise ValueError("Pokémon must have between 1 and 4 moves, but has %d" % len(moves_raw))
    for move_raw in moves_raw:
        move = []
        if not isinstance(move_raw, list):
            move_raw = [move_raw]
        for move_raw_single in move_raw:
            pp = None
            pp_ups = 0
            # move might have pp-up and fixed pp information
            pp_info = re.search(r"\(\+\d+\)|\(=\d+\)|\(\+\d+\/=\d+\)$", move_raw_single)
            if pp_info:
                move_raw_single = move_raw_single[:pp_info.start()-1]
                for bit in pp_info.group(0).strip("()").split("/"):
                    if bit.startswith("+"):
                        pp_ups = int(bit[1:])
                    elif bit.startswith("="):
                        pp = int(bit[1:])
            move_single, perfect_match = _get_by_index_or_name(gen4data.MOVES, move_raw_single, "move", gen4data.get_move, gen4data.find_move)
            if not perfect_match:
                warn("Didn't recognize move %s, but assumed %s." % (move_raw_single, move_single["name"]))
            move_single["pp_ups"] = pp_ups
            pp = pp or move_single["pp"]
            pp = int(pp * (1 + 0.2 * pp_ups))
            move_single["pp"] = pp

            # extra displayname, might differ due to special cases
            move_single["displayname"] = move_single["name"]

            # special case: Hidden Power. Fix type, power and displayname
            if move_single["name"] == "Hidden Power":
                a, b, c, d, e, f = [ivs[stat]%2 for stat in ("hp", "atk", "def", "spe", "spA", "spD")]
                hp_type = ((a + 2*b + 4*c + 8*d + 16*e + 32*f)*15) // 63
                move_single["type"] = ("Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark")[hp_type]
                u, v, w, x, y, z = [(ivs[stat]>>1)%2 for stat in ("hp", "atk", "def", "spe", "spA", "spD")]
                hp_power = ((u + 2*v + 4*w + 8*x + 16*y + 32*z) * 40)//63 + 30
                move_single["power"] = hp_power
                move_single["displayname"] = "HP {} [{}]".format(hp_type, hp_power)
            # special case: Return and Frustration. Fix power and displayname
            elif move_single["name"] == "Return":
                move_single["power"] = max(1, int(pokeset["happiness"] / 2.5))
                move_single["displayname"] += " [{}]".format(move_single["power"])
            elif move_single["name"] == "Frustration":
                move_single["power"] = max(1, int((255 - pokeset["happiness"]) / 2.5))
                move_single["displayname"] += " [{}]".format(move_single["power"])
            # special case: Natural Gift. Fix power, type and displayname
            elif move_single["name"] == "Natural Gift":
                # TODO make Natural Gift work with item-list
                if len(item) > 1:
                    raise ValueError("Pokémon with Natural Gift as move option currently must have a fixed item")
                ng_type, ng_power = gen4data.NATURAL_GIFT_EFFECTS.get(item[0], ["Normal", 0])
                move_single["power"] = ng_power
                move_single["type"] = ng_type
                move_single["displayname"] = "NG {} [{}]".format(ng_type, ng_power)
            # special case: Judgment. fix type and displayname
            elif move_single["name"] == "Judgment":
                # TODO make Judgment work with item-list
                if len(item) > 1:
                    raise ValueError("Pokémon with Judgment as move option currently must have a fixed item")
                judgment_type = forms.get_multitype_type(item[0])
                move_single["type"] = judgment_type
                move_single["displayname"] += " " + judgment_type

            move.append(move_single)
        moves.append(move)
    pokeset["moves"] = moves

    # check rarity
    rarity = pokeset["rarity"]
    if not (isinstance(rarity, (int, float)) and rarity >= 0.0):
        raise ValueError("rarity must be a number greater or equal to 0.0")
    if rarity > 10.0:
        warn("rarity is %d, which is surprisingly high. Note that 1.0 is the default "
             "and high values mean the Pokémon gets chosen more often." % rarity)

    # fix default biddable value
    if pokeset["biddable"] is None:
        pokeset["biddable"] = not pokeset["shiny"]
    if pokeset["biddable"] and pokeset["shiny"]:
        warn("Set is shiny, but also biddable, which means it is not secret "
             "and usable in token matches at any time. Is this intended?")

    # fix displayname
    if pokeset["displayname"] is None:
        pokeset["displayname"] = pokeset["species"]["name"]
        # formnames get handled below

    # check form
    form = pokeset["form"]
    if not isinstance(form, int):
        formnumber = forms.get_formnumber(species["id"], form)
        if formnumber is None:
            raise ValueError("Unrecognized form %s for species %s" % (form, species["name"]))
        form = formnumber
    formname = forms.get_formname(species["id"], form)
    if formname is None and form != 0:
        raise ValueError("Species %s has no form %s." % (species["name"], form))

    # special case: all forms. fix displayname
    formname = forms.get_formname(species["id"], form)
    if formname:
        pokeset["displayname"] += " " + formname

    # special case: Deoxys. Fix basestats and displayname
    if species["name"] == "Deoxys":
        deoxys_form = forms.get_formname(species["id"], form)
        species["basestats"] = gen4data.DEOXYS_BASESTATS[deoxys_form]
        pokeset["displayname"] += " " + deoxys_form

    # special case: Arceus. Handle as form. Also fix type
    if species["name"] == "Arceus":
        if len(item) > 1:
            raise ValueError("Arceus currently must have a fixed item")
        arceus_type = forms.get_multitype_type(item[0])
        pokeset["types"] = [arceus_type]
        pokeset["displayname"] += " " + arceus_type
        pokeset["form"] = gen4data.TYPES.index(arceus_type)

    # special case: Wormadam. Fix type
    if species["name"] == "Wormadam":
        wormadam_types = ("Grass", "Ground", "Steel")
        pokeset["types"] = ["Bug", wormadam_types[form]]

    # add stats
    pokeset["stats"] = {}
    for statname in stats.statnames:
        basestat = species["basestats"][statname]
        ev = evs[statname]
        iv = ivs[statname]
        nature_id = nature["id"]
        level = pokeset["level"]
        pokeset["stats"][statname] = stats.calculate_stat(basestat, ev, iv, statname, nature_id, level)

    # special case: Shedinja. Always 1 HP
    if species["name"] == "Shedinja":
        pokeset["stats"]["hp"] = 1

    # add shininess to display name
    if pokeset["shiny"]:
        pokeset["displayname"] += " (Shiny)"

    # check combinations and separations
    combinations = pokeset["combinations"]
    if not isinstance(combinations, list) and not all(isinstance(c, list) for c in combinations):
        raise ValueError("combinations must be a list of lists.")
    separations = pokeset["separations"]
    if not isinstance(separations, list) and not all(isinstance(s, list) for s in separations):
        raise ValueError("separations must be a list of lists.")
    movenames = sum([movelist for movelist in pokeset["moves"]], [])
    movenames = [move["name"] for move in movenames]
    all_things = set(movenames + pokeset["item"] + pokeset["ability"])
    for com in combinations:
        if set(com) - all_things:
            raise ValueError("All things referenced in combination must be present in set: %s" % ", ".join(com))
    for sep in separations:
        if set(sep) - all_things:
            raise ValueError("All things referenced in separation must be present in set: %s" % ", ".join(sep))
    # TODO tolerate spelling mistakes. Levenshtein
    # TODO validate that the combinations and separations even allow for a functioning set to be generated

    return pokeset


def _check_restrictions(pokeset):
    '''
    Checks if the "Combinations" and "Separations" defined in a set are respected.
    Returns True if they are, and False otherwise.
    '''
    movenames = [m["name"] for m in pokeset["moves"]]
    all_things = frozenset(movenames + [pokeset["item"]] + [pokeset["ability"]])
    for combination in pokeset["combinations"]:
        # all or nothing
        valid = all(thing in all_things for thing in combination) \
                or not any(thing in all_things for thing in combination)
        if not valid:
            return False
    for separation in pokeset["separations"]:
        # can never be more than one
        valid = sum(int(thing in all_things) for thing in separation) <= 1
        if not valid:
            return False
    return True


def instantiate_pokeset(pokeset):
    '''
    Takes a populated set and solidifies any data that is ought to be decided by RNG.
    This includes randomly picking from lists of genders, abilities, items and/or moves.
    The "Combinations" and "Separations" rules are taken into consideration.

    Returns:
        The instantiated set
    '''
    def instantiate(item, key):
        item[key] = random.choice(item[key])
    # brute-force valid set by rerolling until it is valid (sorry...)
    attempts = 0x2329  # random high number
    for _ in range(attempts):
        instance = deepcopy(pokeset)
        instantiate(instance, "item")
        instantiate(instance, "ball")
        instantiate(instance, "ability")
        instantiate(instance, "gender")
        for move_i in range(len(instance["moves"])):
            instantiate(instance["moves"], move_i)
        if _check_restrictions(instance):
            del instance["combinations"]
            del instance["separations"]
            return instance
    log.critical("Was unable to generate instance of set that respects the "
                 "restrictions after %d attempts. Moveset: %s", attempts, pokeset)
    del instance["combinations"]
    del instance["separations"]
    return instance  # invalid instance though :(
