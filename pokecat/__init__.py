
import logging
import random
import re
from collections import Counter
from copy import deepcopy
from difflib import ndiff
from itertools import chain
from warnings import warn
from unidecode import unidecode

from Levenshtein import ratio

from .utils import normalize_name
from . import gen1data, gen4data, forms, stats
from . import utils, objects
from .suppress import Suppressions

log = logging.getLogger(__name__)

_OBLIGATORY_FIELDS = {"setname", "species", "nature", "ivs", "evs", "moves"}
_OPTIONAL_FIELDS = {"ability": None, "ingamename": None, "gender": None, "form": 0, "item": None, "displayname": None,
                    "happiness": 255, "shiny": False, "biddable": None, "hidden": None, "rarity": 1.0, "ball": "Poké",
                    "level": 100, "combinations": [], "separations": [], "tags": [], "suppressions": []}
_GLOBAL_SUPPRESSIONS = {Suppressions.WASTED_EVS}

def is_difference_significant(name1, name2):
    name1, name2 = unidecode(name1.lower()), unidecode(name2.lower())
    diff_chars = {d[-1] for d in ndiff(name1, name2) if d[0] in "+-"}
    insignificant_chars = set("- ")
    if diff_chars - insignificant_chars:
        # remaining chars => significant difference
        return True
    return False


# just code recycling for populate_pokeset()
def _get_by_index_or_name(lst, index_or_name, name_of_thing, get_func, find_func):
    if isinstance(index_or_name, int):
        try:
            thing = lst[index_or_name]
        except IndexError:
            raise ValueError("Invalid %s number: %d" % (name_of_thing, index_or_name))
    else:
        thing = get_func(index_or_name)
        if not thing:
            candidates = find_func(index_or_name)
            if not candidates:
                raise ValueError("Unrecognized %s: %s" % (name_of_thing, index_or_name))
            if len(candidates) > 1:
                raise ValueError("Unrecognized %s: %s, autocorrection was ambiguous: %s"
                                 % (name_of_thing, index_or_name, ", ".join(n["name"] for n in candidates.values())))
            thing = next(iter(candidates.values()))
            # special case: "ball" is not appended for balls
            if name_of_thing == "ball":
                index_or_name += " ball"
            return deepcopy(thing), not is_difference_significant(index_or_name, thing["name"])
    return deepcopy(thing), True


def populate_pokeset(pokeset, skip_ev_check=False):
    """
    Reads in data for one pokeset and populates it with all additionally available
    data. This includes types of Pokémon or per-move data like PP, power or types.

    Arguments:
        pokeset: base data of the set to populate. see the format specification for details.
        skip_ev_check: Defaults to False. If True, allows illegal movesets (produces a
                       warning instead of an error)
    Throws:
        ValueError: If the data is not fully parsable. the ValueError's description contains
        further details on the error that occured.
    Returns:
        The populated set. The passed data is not modified
    """
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
            pokeset[key] = deepcopy(default)

    # parse suppressions
    suppressions = set()
    for suppression_str in pokeset["suppressions"]:
        try:
            suppression = Suppressions(suppression_str)
        except ValueError:
            raise ValueError("{} is not a recognized suppression.".format(suppression_str))
        else:
            if suppression in suppressions:
                raise ValueError("Suppression is specified twice: {}".format(suppression.value))
            suppressions.add(suppression)
    # don't actually include suppressions in the data
    del pokeset["suppressions"]
    suppressions |= _GLOBAL_SUPPRESSIONS

    # check validity of names
    if not pokeset["setname"] or not isinstance(pokeset["setname"], str):
        raise ValueError("setname must be a non-empty string")
    custom_displayname = False
    if pokeset["displayname"] is not None:
        custom_displayname = True
        if not pokeset["displayname"] or not isinstance(pokeset["displayname"], str):
            raise ValueError("displayname, if set, must be a non-empty string")

    # check and populate species
    species_raw = pokeset["species"]
    if species_raw is None:
        raise ValueError("Invalid species: %s" % (species_raw,))
    species, perfect_match = _get_by_index_or_name(gen4data.POKEDEX, species_raw,
                                                   "species", gen4data.get_pokemon, gen4data.find_pokemon)
    if not perfect_match:
        warn("Didn't recognize species %s, but assumed %s." % (species_raw, species["name"]))
    pokeset["species"] = species

    # check tags
    tags = pokeset["tags"]
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("tags must be a list of strings")
    pokeset["tags"] = tags

    # replace None-default for ingamename
    if pokeset["ingamename"] is None:
        pokeset["ingamename"] = species["name"].upper()
    # check length of ingamename
    if not 1 <= len(pokeset["ingamename"]) <= 10:
        raise ValueError("ingamename must be between 1 and 10 characters long: %s" % pokeset["ingamename"])

    # check happiness
    if not isinstance(pokeset["happiness"], int):
        raise ValueError("happiness must be a number.")

    # check and populate ability. is a list
    ability = []
    ability_raw = pokeset["ability"]
    if not isinstance(ability_raw, list):
        ability_raw = [ability_raw]
    if not ability_raw:
        raise ValueError("List of possible abilities cannot be empty.")
    for ability_raw_single in ability_raw:
        ability_single, perfect_match = _get_by_index_or_name(gen4data.ABILITIES, ability_raw_single,
                                                              "ability", gen4data.get_ability, gen4data.find_ability)
        if not perfect_match:
            warn("Didn't recognize ability %s, but assumed %s." % (ability_raw_single, ability_single["name"]))
        ability.append(ability_single)
    if len(set(a["id"] for a in ability)) < len(ability):
        raise ValueError("All abilities supplied must be unique: %s" % ", ".join(a["name"] for a in ability))
    pokeset["ability"] = ability

    # check and populate item. is a list
    item = []
    item_raw = pokeset["item"]
    if not isinstance(item_raw, list):
        item_raw = [item_raw]
    if not item_raw:
        raise ValueError("List of possible items cannot be empty.")
    for item_raw_single in item_raw:
        item_single, perfect_match = _get_by_index_or_name(gen4data.ITEMS, item_raw_single,
                                                           "item", gen4data.get_item, gen4data.find_item)
        if not perfect_match:
            warn("Didn't recognize item %s, but assumed %s." % (item_raw_single, item_single["name"]))
        item.append(item_single)
    if len(set(i["id"] for i in item)) < len(item):
        raise ValueError("All items supplied must be unique: %s" % ", ".join(i["name"] for i in item))
    pokeset["item"] = item

    # check and populate ball. is a list
    ball = []
    ball_raw = pokeset["ball"]
    if not isinstance(ball_raw, list):
        ball_raw = [ball_raw]
    if not ball_raw:
        raise ValueError("List of possible balls cannot be empty.")
    for ball_raw_single in ball_raw:
        ball_single, perfect_match = _get_by_index_or_name(gen4data.ITEMS, ball_raw_single,
                                                           "ball", gen4data.get_ball, gen4data.find_ball)
        if not ball_single["name"].endswith(" Ball"):
            raise ValueError("Invalid ball: %s" % ball_single)
        if not perfect_match:
            warn("Didn't recognize ball %s, but assumed %s." % (ball_raw_single, ball_single["name"]))
        ball.append(ball_single)
    if len(set(b["name"] for b in ball)) < len(ball):
        raise ValueError("All balls supplied must be unique: %s" % ", ".join(b["name"] for b in ball))
    pokeset["ball"] = ball

    # check gender
    gender = pokeset["gender"]
    if not isinstance(gender, list):
        gender = [gender]
    if not gender:
        raise ValueError("List of possible genders cannot be empty.")
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
    if not isinstance(nature_raw, str):
        raise ValueError("Invalid nature: %s" % (nature_raw,))
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
    if not isinstance(ivs, dict):
        raise ValueError("Invalid IVs: %s" % (ivs,))
    if set(stats.statnames) != set(ivs.keys()):
        raise ValueError("ivs must contain the following keys: %s" % ", ".join(stats.statnames))
    if not all(isinstance(v, int) for v in ivs.values()):
        raise ValueError("Invalid IV value in IVs: %s" % (ivs,))
    if not all(0 <= val <= 31 for val in ivs.values()):
        raise ValueError("All IVs must be between 0 and 31.")
    pokeset["ivs"] = ivs
    # check EVs
    evs = pokeset["evs"]
    if isinstance(evs, int):
        evs = {name: evs for name in stats.statnames}
    if not isinstance(evs, dict):
        raise ValueError("Invalid EVs: %s" % (evs,))
    if set(stats.statnames) != set(evs.keys()):
        raise ValueError("evs must contain the following keys: %s" % ", ".join(stats.statnames))
    if not all(isinstance(v, int) for v in evs.values()):
        raise ValueError("Invalid EV value in EVs: %s" % (evs,))
    if not all(0 <= val for val in evs.values()):
        raise ValueError("All EVs must be >= 0.")
    if not all(val <= 252 for val in evs.values()) and Suppressions.INVALID_EVS not in suppressions:
        message = "All EVs must be <= 252."
        if skip_ev_check:
            warn(message)
        else:
            raise ValueError(message)
    ev_sum = sum(val for val in evs.values())
    if ev_sum > 510 and Suppressions.INVALID_EVS not in suppressions:
        message = "Sum of EV must not be larger than 510, but is %d" % ev_sum
        if skip_ev_check:
            warn(message)
        else:
            raise ValueError(message)
    for key, value in evs.items():
        if value % 4 != 0 and Suppressions.WASTED_EVS not in suppressions:
            warn("EV for %s is %d, which is not a multiple of 4 (wasted points)" % (key, value))
    pokeset["evs"] = evs

    # TODO outsorce singular move procession
    # check and populate moves
    moves = []
    moves_raw = pokeset["moves"]
    if not 1 <= len(moves_raw) <= 4:
        raise ValueError("Pokémon must have between 1 and 4 moves, but has %d" % len(moves_raw))
    guaranteed_moves_ids = []
    for slot_index, move_raw in enumerate(moves_raw):
        move = []
        if not isinstance(move_raw, list):
            move_raw = [move_raw]
        if not move_raw:
            raise ValueError("List of possible moves in slot {} cannot be empty.".format(slot_index+1))
        for move_raw_single in move_raw:
            pp = None
            pp_ups = 0
            # move might have pp-up and fixed pp information
            pp_info = re.search(r"\(\+\d+\)|\(=\d+\)|\(\+\d+/=\d+\)$", move_raw_single)
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
            move.append(move_single)
        if len(move) == 1 and Suppressions.DUPLICATE_MOVES not in suppressions:
            move_id = move[0]["id"]
            if guaranteed_moves_ids.count(move_id) == 1:
                warn("Move {} is guaranteed to occupy multiple slots (possible stallmate due to PP-bug).".format(move[0]["name"]))
            guaranteed_moves_ids.append(move_id)
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
    if not isinstance(pokeset["biddable"], bool):
        raise ValueError("biddable must be a boolean (true or false), not %s" % type(pokeset["biddable"]))

    # fix default hidden value
    if pokeset["hidden"] is None:
        pokeset["hidden"] = pokeset["shiny"]
    if not isinstance(pokeset["hidden"], bool):
        raise ValueError("hidden must be a boolean (true or false), not %s" % type(pokeset["hidden"]))

    if pokeset["biddable"] and pokeset["hidden"]:
        warn("Set is biddable, but also hidden, which doesn't make sense.")
    if pokeset["shiny"] and pokeset["biddable"] and Suppressions.PUBLIC_SHINY not in suppressions:
        warn("Set is shiny, but also biddable, which means it can be used in token matches. Is this intended?")
    if pokeset["shiny"] and not pokeset["hidden"] and Suppressions.PUBLIC_SHINY not in suppressions:
        warn("Set is shiny, but not hidden, which means it is publicly visible. Is this intended?")

    # fix displayname
    if pokeset["displayname"] is None:
        pokeset["displayname"] = pokeset["species"]["name"]
        # formnames get handled below

    # check form
    form = pokeset["form"]
    if not isinstance(form, int):
        if not isinstance(form, str):
            raise ValueError("form must be a formnumber or a string, not %s" % type(form))
        formnumber = forms.get_formnumber(species["id"], form)
        if formnumber is None:
            raise ValueError("Unrecognized form %s for species %s" % (form, species["name"]))
        form = formnumber
    pokeset["form"] = form
    formname = forms.get_formname(species["id"], form)
    if formname is None and form != 0:
        raise ValueError("Species %s has no form %s." % (species["name"], form))

    apply_pokeset_form_adjustments(pokeset)

    # add stats
    pokeset["stats"] = {}
    for statname in stats.statnames:
        basestat = species["basestats"][statname]
        ev = evs[statname]
        iv = ivs[statname]
        level = pokeset["level"]
        pokeset["stats"][statname] = stats.calculate_stat(basestat, ev, iv, statname, nature, level)

    # special case: Shedinja. Always 1 HP
    if species["name"] == "Shedinja":
        pokeset["stats"]["hp"] = 1

    # add autogenerated tags
    if pokeset["biddable"]:
        pokeset["tags"].append("biddable")
    if pokeset["hidden"]:
        pokeset["tags"].append("hidden")
    if pokeset["shiny"]:
        pokeset["tags"].append("shiny")
    pokeset["tags"].append("species+%d" % pokeset["species"]["id"])
    pokeset["tags"].append("species+%s" % pokeset["species"]["name"])
    for type_ in pokeset["species"]["types"]:
        pokeset["tags"].append("type+%s" % type_)
    pokeset["tags"].append("color+%s" % pokeset["species"]["color"])
    pokeset["tags"].append("level+%d" % pokeset["level"])
    pokeset["tags"].append("form+%d" % pokeset["form"])

    for ability_ in pokeset["ability"]:
        if ability_:
            pokeset["tags"].append("ability+%s" % str(ability_["name"]))
    pokeset["tags"].append("setname+%s" % pokeset["setname"])

    # ensure no duplicate tags
    pokeset["tags"] = sorted(set(pokeset["tags"]))

    # check combinations and separations
    combinations = pokeset["combinations"]
    if not isinstance(combinations, list) or not all(isinstance(c, list) for c in combinations):
        raise ValueError("combinations must be a list of lists.")
    if not all(isinstance(s, str) or s is None for s in chain(*combinations)):
        raise ValueError("combination items must be strings or null")
    separations = pokeset["separations"]
    if not isinstance(separations, list) or not all(isinstance(s, list) for s in separations):
        raise ValueError("separations must be a list of lists.")
    if not all(isinstance(s, str) or s is None for s in chain(*separations)):
        raise ValueError("separation items must be strings or null")
    movenames = sum([movelist for movelist in pokeset["moves"]], [])
    movenames = list(set(move["name"] for move in movenames))
    all_things = (movenames
                  + [p["name"] for p in pokeset["item"]]
                  + [a["name"] for a in pokeset["ability"]])
    ambiguities = set(item for item, count in Counter(all_things).items() if count > 1)
    all_things = set(all_things)
    for com in combinations:
        if any(c in ambiguities for c in com):
            raise ValueError("Can't use %s in combinations, as it is ambiguous." % (com,))
        rest = [item for item in com if item not in all_things]
        for r in list(rest):
            if not r:
                continue
            for thing in all_things - {None}:
                if ratio(thing.lower(), r.lower()) > 0.9:
                    if is_difference_significant(thing, r):
                        warn("Didn't recognize combination %s, but assumed %s." % (r, thing))
                    rest.remove(r)
                    com.remove(r)
                    com.append(thing)
                    break
        if rest:
            raise ValueError("All things referenced in combination must be present in set. Missing: %s" % ", ".join(rest))
    for sep in separations:
        if any(s in ambiguities for s in sep):
            raise ValueError("Can't use %s in separations, as it is ambiguous." % (sep,))
        rest = [item for item in sep if item not in all_things]
        for r in list(rest):
            if not r:
                continue
            for thing in all_things - {None}:
                if ratio(thing.lower(), r.lower()) > 0.9:
                    if is_difference_significant(thing, r):
                        warn("Didn't recognize separation %s, but assumed %s." % (r, thing))
                    rest.remove(r)
                    sep.remove(r)
                    sep.append(thing)
                    break
        if rest:
            raise ValueError("All things referenced in separation must be present in set. Missing: %s" % ", ".join(rest))
    # TODO validate that the combinations and separations even allow for a functioning set to be generated
    return pokeset


def apply_pokeset_form_adjustments(pokeset):
    form = pokeset["form"]
    species = pokeset["species"]

    custom_displayname = False
    if (pokeset["displayname"] is not None and
            pokeset["displayname"] != species["name"]):
        custom_displayname = True

    # special case: all forms. fix displayname
    formname = forms.get_formname(species["id"], form)
    if formname and not custom_displayname:
        pokeset["displayname"] =  species["name"] + " " + formname

    # special case: Deoxys. Fix basestats (displayname already fixed)
    if species["name"] == "Deoxys":
        deoxys_form = forms.get_formname(species["id"], form)
        species["basestats"] = gen4data.DEOXYS_BASESTATS[deoxys_form]
        recalculate_pokeset_stats(pokeset)
    elif species["name"] == "Wormadam":
        wormadam_form = forms.get_formname(species["id"], form)
        species["basestats"] = gen4data.WORMADAM_BASESTATS[wormadam_form]
        recalculate_pokeset_stats(pokeset)

    # special case: Wormadam. Fix type
    if species["name"] == "Wormadam":
        wormadam_types = ("Grass", "Ground", "Steel")
        pokeset["species"]["types"] = ["Bug", wormadam_types[form]]

    if species["name"] in ["Burmy", "Wormadam"]:
        colors = ("Green", "Brown", "Pink")
        pokeset["species"]["color"] = colors[form]

    if species["name"] in ["Shellos", "Gastrodon"]:
        colors = ("Pink", "Blue")
        pokeset["species"]["color"] = colors[form]

    # special case: Arceus. Handle as form. Also fix type
    if species["name"] == "Arceus":
        if "ability" in species and species["ability"]["name"] != "Multitype":
            pokeset["species"]["types"] = ["Normal"]
            if not custom_displayname:
                pokeset["displayname"] = species["name"]
        else:
            item = pokeset["item"]
            if type(item) is list:
                if len(item) > 1:
                    raise ValueError("Arceus currently must have a fixed item")
                item = item[0]
            arceus_type = forms.get_multitype_type(item)
            pokeset["species"]["types"] = [arceus_type]
            arceus_color = forms.get_multitype_color(item)
            pokeset["species"]["color"] = [arceus_color]
            if not custom_displayname:
                pokeset["displayname"] = species["name"] + " " + arceus_type


def _check_restrictions(pokeset):
    """
    Checks if the "Combinations" and "Separations" defined in a set are respected.
    Returns True if they are, and False otherwise.
    """
    movenames = [m["name"] for m in pokeset["moves"]]
    all_things = movenames + [pokeset["item"]["name"]] + [pokeset["ability"]["name"]]
    for combination in pokeset["combinations"]:
        things = all_things[:]
        missing_count = 0
        for com in combination:
            try:
                things.remove(com)
            except ValueError:
                missing_count += 1
        # all or nothing
        if 0 < missing_count < len(combination):
            return False
    for separation in pokeset["separations"]:
        # can never be more than one
        things = all_things[:]
        present_count = 0
        for sep in separation:
            try:
                things.remove(sep)
            except ValueError:
                pass
            else:
                present_count += 1
                if present_count > 1:
                    return False
    return True


def instantiate_pokeset(pokeset):
    """
    Takes a populated set and solidifies any data that is ought to be decided by RNG.
    This includes randomly picking from lists of genders, abilities, items and/or moves.
    The "Combinations" and "Separations" rules are taken into consideration.

    Returns:
        The instantiated set
    """
    def instantiate(item, key):
        item[key] = random.choice(item[key])
    def fix_moves(instance):
        ivs = instance["ivs"]
        for move in instance["moves"]:
            # extra displayname, might differ due to special cases
            move["displayname"] = move["name"]
            
            # special case: Hidden Power. Fix type, power and displayname
            if move["name"] == "Hidden Power":
                a, b, c, d, e, f = [ivs[stat] % 2 for stat in ("hp", "atk", "def", "spe", "spA", "spD")]
                hp_type = ((a + 2*b + 4*c + 8*d + 16*e + 32*f)*15) // 63
                move["type"] = ("Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark")[hp_type]
                u, v, w, x, y, z = [(ivs[stat] >> 1) % 2 for stat in ("hp", "atk", "def", "spe", "spA", "spD")]
                hp_power = ((u + 2*v + 4*w + 8*x + 16*y + 32*z) * 40)//63 + 30
                move["power"] = hp_power
                move["displayname"] = "HP {} [{}]".format(move["type"], hp_power)
            # special case: Return and Frustration. Fix power and displayname
            elif move["name"] == "Return":
                move["power"] = max(1, int(instance["happiness"] / 2.5))
                move["displayname"] += " [{}]".format(move["power"])
            elif move["name"] == "Frustration":
                move["power"] = max(1, int((255 - instance["happiness"]) / 2.5))
                move["displayname"] += " [{}]".format(move["power"])
            # special case: Natural Gift. Fix power, type and displayname
            elif move["name"] == "Natural Gift":
                ng_type, ng_power = gen4data.NATURAL_GIFT_EFFECTS.get(instance["item"]["name"], ["Normal", 0])
                move["power"] = ng_power
                move["type"] = ng_type
                move["displayname"] = "NG {} [{}]".format(ng_type, ng_power)
            # special case: Judgment. fix type and displayname
            elif move["name"] == "Judgment":
                judgment_type = forms.get_multitype_type(instance["item"])
                move["type"] = judgment_type
                move["displayname"] += " " + judgment_type
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
            fix_moves(instance)
            return instance
    log.critical("Was unable to generate instance of set that respects the "
                 "restrictions after %d attempts. Moveset: %s", attempts, pokeset)
    del instance["combinations"]
    del instance["separations"]
    fix_moves(instance)
    return instance  # invalid instance though :(


def generate_random_pokeset():
    pokeset = {}
    pokeset["species"] = random.randint(1, 493)
    pokeset["setname"] = "Standard"
    pokeset["ability"] = random.choice(gen4data.ABILITIES)["name"]
    pokeset["nature"]  = random.choice(gen4data.NATURES)["name"]
    pokeset["ivs"]     = {stat: random.randint(1, 31) for stat in stats.statnames}
    pokeset["evs"]     = {stat: random.randint(0, 85//4)*4 for stat in stats.statnames}
    random_moves       = random.sample(gen4data.MOVES,
                                       random.choice([4, 4, 4, 4, 4, 3, 2, 1, 1]))
    pokeset["moves"]   = [m["name"] for m in random_moves]
    pokeset["shiny"]   = random.random() < 0.2
    if random.random() < 0.3:
        pokeset["item"] = random.choice(gen4data.ITEMS)["name"]
    if random.random() < 0.8:
        pokeset["gender"] = random.choice(["m", "f"])
    return populate_pokeset(pokeset)

def generate_random_pokemon():
    pokeset = generate_random_pokeset()
    return instantiate_pokeset(pokeset)


def recalculate_pokeset_stats(pokeset):
    """Perform whenever a pokeset's base stats, evs, etc. are changed."""
    for statname in stats.statnames:
        if 'stats' in pokeset:
            pokeset['stats'][statname] = stats.calculate_stat(
                pokeset['species']['basestats'][statname],
                pokeset['evs'][statname],
                pokeset['ivs'][statname],
                statname,
                pokeset['nature'],
                pokeset['level']
            )


def redact_pokeset_data(pokemon):
    pokemon['displayname'] = '???'
    pokemon['ingamename'] = '???'
    pokemon['setname'] = '???'
    pokemon['gender'] = None
    pokemon['form'] = 0
    pokemon['happiness'] = 0
    pokemon['level'] = 100
    pokemon['biddable'] = True
    pokemon['ability']['id'] = 0
    pokemon['ability']['name'] = '???'
    pokemon['ability']['description'] = ''
    pokemon['item']['id'] = 0
    pokemon['item']['name'] = '???'
    pokemon['item']['description'] = ''
    pokemon['ball']['id'] = 0
    pokemon['ball']['name'] = '???'
    pokemon['ball']['description'] = ''
    pokemon['nature']['id'] = 0
    pokemon['nature']['name'] = '???'
    pokemon['nature']['increased'] = None
    pokemon['nature']['decreased'] = None
    pokemon['species']['id'] = 0
    pokemon['species']['name'] = '???'
    pokemon['species']['types'] = ['???']
    pokemon['stats'] = {
        'hp': '???',
        'atk': '???',
        'def': '???',
        'spA': '???',
        'spD': '???',
        'spe': '???',
    }
    pokemon['species']['basestats'] = pokemon['stats']
    pokemon['original_species']['id'] = 0
    pokemon['original_species']['name'] = '???'
    pokemon['original_species']['types'] = ['???']
    pokemon['original_species']['basestats'] = pokemon['stats']
    pokemon['ivs'] = pokemon['stats']
    pokemon['evs'] = pokemon['stats']
    pokemon['rarity'] = 1.0
    pokemon['moves'] = pokemon['moves'][:1]
    pokemon['moves'][0]['id'] = 0
    pokemon['moves'][0]['displayname'] = '???'
    pokemon['moves'][0]['name'] = '???'
    pokemon['moves'][0]['name_id'] = '???'
    pokemon['moves'][0]['category'] = 'Physical'
    pokemon['moves'][0]['type'] = '???'
    pokemon['moves'][0]['pp'] = 0
    pokemon['moves'][0]['pp_ups'] = 0
    pokemon['moves'][0]['power'] = 0
    pokemon['moves'][0]['accuracy'] = 0
    pokemon['tags'] = []

