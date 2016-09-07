
import os
import unittest
import json
import yaml

import pokecat

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
def load_test_docs(name):
    path = os.path.join(ROOT_DIR, "testdocuments", "{}.yaml".format(name))
    return list(yaml.load_all(open(path, encoding="utf-8")))
def load_test_doc(name):
    path = os.path.join(ROOT_DIR, "testdocuments", "{}.yaml".format(name))
    return yaml.load(open(path, encoding="utf-8"))
def load_test_doc_json(name):
    path = os.path.join(ROOT_DIR, "testdocuments", "{}.json".format(name))
    return json.load(open(path, encoding="utf-8"))


class PokecatTester(unittest.TestCase):
    def test_load(self):
        # just make sure loading the testdocs even works
        doc = load_test_doc("dummy")
        self.assertEqual(doc, {"a":1, "b":"a", "c":None})

    def test_warning_lowercase_keys(self):
        doc = load_test_doc("_template")
        doc["Ingamename"] = doc["ingamename"]
        del doc["ingamename"]
        with self.assertWarnsRegex(UserWarning, r"Key should be all lowercase: Ingamename"):
            pokecat.populate_pokeset(doc)

    def test_fields_missing(self):
        doc = load_test_doc("_template")
        del doc["evs"]
        with self.assertRaisesRegex(ValueError, r"pokeset is missing obligatory fields: evs"):
            pokecat.populate_pokeset(doc)

    def test_unknown_fields(self):
        doc = load_test_doc("_template")
        doc["foobar"] = 1
        with self.assertRaisesRegex(ValueError, r"pokeset has unrecognized fields: foobar"):
            pokecat.populate_pokeset(doc)

    def test_too_long_ingamename(self):
        doc = load_test_doc("_template")
        doc["ingamename"] = "BULBASAURRRR"
        with self.assertRaisesRegex(ValueError, r"ingamename must be between 1 and 10 characters long: BULBASAURRRR"):
            pokecat.populate_pokeset(doc)

    def test_empty_setname(self):
        doc = load_test_doc("_template")
        doc["setname"] = ""
        with self.assertRaisesRegex(ValueError, r"setname must be a non-empty string"):
            pokecat.populate_pokeset(doc)

    def test_optional_fields_overwrite(self):
        # test if supplied optional fields don't get overwritten.
        # just test with rarity
        doc = load_test_doc("_template")
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["rarity"], 1.0)
        doc["rarity"] = 4.2
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["rarity"], 4.2)

    def test_species_number(self):
        doc = load_test_doc("_template")
        doc["species"] = 151
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["species"]["name"], "Mew")

    def test_species_name(self):
        doc = load_test_doc("_template")
        doc["species"] = "Mew"
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["species"]["id"], 151)

    def test_invalid_species_number(self):
        doc = load_test_doc("_template")
        doc["species"] = 494  # Victini, not gen 4
        with self.assertRaisesRegex(ValueError, r"Invalid species number: 494"):
            pokecat.populate_pokeset(doc)

    def test_misspelled_species_name(self):
        doc = load_test_doc("_template")
        doc["species"] = "Groundon"  # common spelling mistake
        with self.assertWarnsRegex(UserWarning, r"Didn't recognize species Groundon, but assumed Groudon."):
            result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["species"]["name"], "Groudon")

    def test_invalid_species_name(self):
        doc = load_test_doc("_template")
        doc["species"] = "BEST"
        with self.assertRaisesRegex(ValueError, r"Unrecognized species: BEST"):
            pokecat.populate_pokeset(doc)

    def test_ability(self):
        doc = load_test_doc("_template")
        doc["ability"] = "Pressure"
        result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual([a["name"] for a in result["ability"]], ["Pressure"])

    def test_ability_list(self):
        doc = load_test_doc("_template")
        doc["ability"] = ["Pressure", "Static"]
        result = pokecat.populate_pokeset(doc)
        self.assertEqual([a["name"] for a in result["ability"]], ["Pressure", "Static"])

    def test_duplicate_ability_list(self):
        doc = load_test_doc("_template")
        doc["ability"] = ["Pressure", "Pressure"]
        with self.assertRaisesRegex(ValueError, r"All abilities supplied must be unique: Pressure, Pressure"):
            pokecat.populate_pokeset(doc)

    def test_misspelled_ability(self):
        doc = load_test_doc("_template")
        doc["ability"] = "Presure"  # some spelling mistake
        with self.assertWarnsRegex(UserWarning, r"Didn't recognize ability Presure, but assumed Pressure."):
            result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual([a["name"] for a in result["ability"]], ["Pressure"])

    def test_invalid_ability(self):
        doc = load_test_doc("_template")
        doc["ability"] = "Invincibility"  # doesn't exist
        with self.assertRaisesRegex(ValueError, "Unrecognized ability: Invincibility"):
            pokecat.populate_pokeset(doc)

    def test_item(self):
        doc = load_test_doc("_template")
        doc["item"] = "Sitrus Berry"
        result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual([i["name"] for i in result["item"]], ["Sitrus Berry"])

    def test_item_list(self):
        doc = load_test_doc("_template")
        doc["item"] = ["Sitrus Berry", "Elixir"]
        result = pokecat.populate_pokeset(doc)
        self.assertEqual([i["name"] for i in result["item"]], ["Sitrus Berry", "Elixir"])

    def test_duplicate_item_list(self):
        doc = load_test_doc("_template")
        doc["item"] = ["Sitrus Berry", "Sitrus Berry"]
        with self.assertRaisesRegex(ValueError, r"All items supplied must be unique: Sitrus Berry, Sitrus Berry"):
            pokecat.populate_pokeset(doc)

    def test_misspelled_item(self):
        doc = load_test_doc("_template")
        doc["item"] = "Citrus Berry"  # some spelling mistake
        with self.assertWarnsRegex(UserWarning, r"Didn't recognize item Citrus Berry, but assumed Sitrus Berry."):
            result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual([i["name"] for i in result["item"]], ["Sitrus Berry"])

    def test_invalid_item(self):
        doc = load_test_doc("_template")
        doc["item"] = "Ice Cream"  # doesn't exist, how sad
        with self.assertRaisesRegex(ValueError, "Unrecognized item: Ice Cream"):
            pokecat.populate_pokeset(doc)

    def test_no_item(self):
        doc = load_test_doc("_template")
        doc["item"] = None
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["item"], [{"id": 0, "description": "", "name": None}])

    def test_ball(self):
        doc = load_test_doc("_template")
        doc["ball"] = "Master"
        result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual([b["name"] for b in result["ball"]], ["Master Ball"])

    def test_ball_list(self):
        doc = load_test_doc("_template")
        doc["ball"] = ["Master", "Ultra"]
        result = pokecat.populate_pokeset(doc)
        self.assertEqual([b["name"] for b in result["ball"]], ["Master Ball", "Ultra Ball"])

    def test_duplicate_ball_list(self):
        doc = load_test_doc("_template")
        doc["ball"] = ["Master", "Master"]
        with self.assertRaisesRegex(ValueError, r"All balls supplied must be unique: Master Ball, Master Ball"):
            pokecat.populate_pokeset(doc)

    def test_misspelled_ball(self):
        doc = load_test_doc("_template")
        doc["ball"] = "Poke"  # missing accent
        with self.assertWarnsRegex(UserWarning, r"Didn't recognize ball Poke, but assumed Poké Ball."):
            result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual([b["name"] for b in result["ball"]], ["Poké Ball"])

    def test_invalid_ball(self):
        doc = load_test_doc("_template")
        doc["ball"] = "Iron"  # Iron Ball isn't a Pokéball
        #with self.assertRaisesRegex(ValueError, "Unrecognized ball: Iron"):
        #    pokecat.populate_pokeset(doc)

    def test_gender(self):
        doc = load_test_doc("_template")
        doc["gender"] = "m"
        result = pokecat.populate_pokeset(doc)
        # gets populated as an array
        self.assertEqual(result["gender"], ["m"])

    def test_gender_list(self):
        doc = load_test_doc("_template")
        doc["gender"] = ["m", "f"]
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["gender"], ["m", "f"])

    def test_duplicate_gender_list(self):
        doc = load_test_doc("_template")
        doc["gender"] = ["m", "m"]
        with self.assertRaisesRegex(ValueError, r"All genders supplied must be unique: m, m"):
            pokecat.populate_pokeset(doc)

    def test_invalid_gender(self):
        doc = load_test_doc("_template")
        doc["gender"] = "w"
        with self.assertRaisesRegex(ValueError, r"gender can only be 'm', 'f' or not set \(null\), but not w"):
            pokecat.populate_pokeset(doc)

    def test_mixed_genders(self):
        doc = load_test_doc("_template")
        doc["gender"] = ["m", None]
        with self.assertRaisesRegex(ValueError, r"non-gender cannot be mixed with m/f"):
            pokecat.populate_pokeset(doc)

    def test_level(self):
        doc = load_test_doc("_template")
        doc["level"] = 100
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["level"], 100)

    def test_invalid_level(self):
        doc = load_test_doc("_template")
        doc["level"] = 101
        with self.assertRaisesRegex(ValueError, r"level must be a number between 1 and 100"):
            pokecat.populate_pokeset(doc)
        doc["level"] = 0
        with self.assertRaisesRegex(ValueError, r"level must be a number between 1 and 100"):
            pokecat.populate_pokeset(doc)

    def test_nature(self):
        doc = load_test_doc("_template")
        doc["nature"] = "Timid"
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["nature"]["name"], "Timid")

    def test_nature_by_effect(self):
        doc = load_test_doc("_template")
        doc["nature"] = "+spA -spe"
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["nature"]["increased"], "spA")
        self.assertEqual(result["nature"]["decreased"], "spe")
        self.assertEqual(result["nature"]["name"], "Quiet")

    def test_misspelled_nature(self):
        doc = load_test_doc("_template")
        doc["nature"] = "Quiot"  # spelling mistake
        with self.assertWarnsRegex(UserWarning, r"Didn't recognize nature Quiot, but assumed Quiet."):
            result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["nature"]["name"], "Quiet")

    def test_invalid_nature(self):
        doc = load_test_doc("_template")
        doc["nature"] = "Brutal"  # doesn't exist
        with self.assertRaisesRegex(ValueError, r"Unrecognized nature: Brutal"):
            pokecat.populate_pokeset(doc)

    def test_ivs_short(self):
        doc = load_test_doc("_template")
        val = 16
        doc["ivs"] = val
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["ivs"], {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val})

    def test_evs_short(self):
        doc = load_test_doc("_template")
        val = 16
        doc["evs"] = val
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["evs"], {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val})

    def test_ivs(self):
        doc = load_test_doc("_template")
        val = 16
        doc["ivs"] = {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val}
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["ivs"], {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val})

    def test_evs(self):
        doc = load_test_doc("_template")
        val = 16
        doc["evs"] = {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val}
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["evs"], {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val})

    def test_missing_iv(self):
        doc = load_test_doc("_template")
        val = 16
        # no hp
        doc["ivs"] = {"atk": val, "def": val, "spA": val, "spD": val, "spe": val}
        with self.assertRaisesRegex(ValueError, r"ivs must contain the following keys: hp, atk, def, spA, spD, spe"):
            pokecat.populate_pokeset(doc)

    def test_missing_ev(self):
        doc = load_test_doc("_template")
        val = 16
        # no atk
        doc["evs"] = {"hp": val, "def": val, "spA": val, "spD": val, "spe": val}
        with self.assertRaisesRegex(ValueError, r"evs must contain the following keys: hp, atk, def, spA, spD, spe"):
            pokecat.populate_pokeset(doc)

    def test_too_many_evs_single(self):
        doc = load_test_doc("_template")
        val = 510
        doc["evs"] = {"atk": val, "def": val, "spA": val, "spD": val, "spe": val}
        doc["evs"]["hp"] = 253
        with self.assertRaisesRegex(ValueError, r"All EVs must be between 0 and 252."):
            pokecat.populate_pokeset(doc)

    def test_too_many_evs_total(self):
        doc = load_test_doc("_template")
        val = 510//6
        doc["evs"] = {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val}
        doc["evs"]["hp"] += 1
        with self.assertRaisesRegex(ValueError, r"Sum of EV must not be larger than 510, but is 511"):
            pokecat.populate_pokeset(doc)

    def test_wasted_evs(self):
        doc = load_test_doc("_template")
        val = 16
        doc["evs"] = {"hp": val, "atk": val, "def": val, "spA": val, "spD": val, "spe": val}
        doc["evs"]["hp"] = 15
        with self.assertWarnsRegex(UserWarning, r"EV for hp is 15, which is not a multiple of 4 \(wasted points\)"):
            pokecat.populate_pokeset(doc)

    def test_rarity(self):
        doc = load_test_doc("_template")
        doc["rarity"] = 0.5
        result = pokecat.populate_pokeset(doc)
        self.assertEqual(result["rarity"], 0.5)

    def test_negative_rarity(self):
        doc = load_test_doc("_template")
        doc["rarity"] = -0.1
        with self.assertRaisesRegex(ValueError, r"rarity must be a number greater or equal to 0.0"):
            pokecat.populate_pokeset(doc)

    # todo test forms, displaynames with forms, moves, special cases, combinations and separations.
    # and whatever isn't tested yet as well


if __name__ == "__main__":
    unittest.main()
