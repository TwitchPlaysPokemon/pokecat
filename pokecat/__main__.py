"""
Usage:
  pokecat populate <inputfile> <outputfile>
  pokecat instantiate <inputfile> <outputfile>
  pokecat genrandom <outputfile> [<amount>]

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import os
from docopt import docopt
import json
import yaml
import warnings
from . import (populate_pokeset,
               instantiate_pokeset,
               generate_random_pokemon)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
__version__ = open(os.path.join(ROOT_DIR, '..', 'VERSION')).read().strip()

def main():
    args = docopt(__doc__, version=__version__)
    if args.get("populate"):
        indata = list(yaml.load_all(open(args["<inputfile>"], encoding="utf-8")))
        outdata = []
        for data in indata:
            if not data:
                continue
            identifier = "{set[species]} {set[setname]}".format(set=data)
            try:
                with warnings.catch_warnings(record=True) as w:
                    data = populate_pokeset(data)
                    for warning in w:
                        print("{}> {}".format(identifier, warning.message))
            except ValueError as ex:
                print("{}> ERROR: {}".format(identifier, ex))
            else:
                outdata.append(data)
        yaml.safe_dump_all(
            outdata,
            open(args["<outputfile>"], "w+", encoding="utf-8"),
            indent=4,
        )
    elif args.get("instantiate"):
        indata = list(yaml.load_all(open(args["<inputfile>"], encoding="utf-8")))
        outdata = []
        for data in indata:
            identifier = "{set[species]} {set[setname]}".format(set=data)
            data = instantiate_pokeset(data)
            outdata.append(data)
        json.dump(
            outdata,
            open(args["<outputfile>"], "w+", encoding="utf-8"),
            indent=4,
        )
    elif args.get("genrandom"):
        num = int(args.get("<amount>") or 1)
        pokemon = [generate_random_pokemon() for _ in range(num)]
        json.dump(
            pokemon,
            open(args["<outputfile>"], "w+", encoding="utf-8"),
            indent=4,
        )


main()
