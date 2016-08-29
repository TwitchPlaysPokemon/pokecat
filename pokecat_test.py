
import os
import unittest
import yaml

import pokecat

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
def load_test_docs(name):
    path = os.path.join(ROOT_DIR, "testdocuments", "{}.yaml".format(name))
    return list(yaml.load_all(open(path, encoding="utf-8")))
def load_test_doc(name):
    path = os.path.join(ROOT_DIR, "testdocuments", "{}.yaml".format(name))
    return yaml.load(open(path, encoding="utf-8"))


class PokecatTester(unittest.TestCase):
    def test_load(self):
        # just make sure loading the testdocs even works
        doc = load_test_doc("dummy")
        self.assertEqual(doc, {"a":1, "b":"a", "c":None})

    def test_warning_lowercase_keys(self):
        doc = load_test_doc("uppercase_key_ingamename")
        with self.assertWarnsRegex(UserWarning, r"Key should be all lowercase: Ingamename"):
            pokecat.populate_pokeset(doc)

    def test_fields_missing(self):
        doc = load_test_doc("field_evs_missing")
        with self.assertRaisesRegex(ValueError, r"pokeset is missing obligatory fields: evs"):
            pokecat.populate_pokeset(doc)

    # TODO write like 100 more tests tomorrow, too tired right now


if __name__ == "__main__":
    unittest.main()
