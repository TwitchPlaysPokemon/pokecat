
import os
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
__version__ = open(os.path.join(ROOT_DIR, 'VERSION')).read().strip()

setup(
    name="pokecat",
    version=__version__,
    packages=find_packages(),
    package_dir={"pokecat": "pokecat"},
    package_data={"pokecat": ["gen4data/*.json", "globaldata/*.json"]},
    data_files=[("", ["VERSION"])],
    install_requires=['pyyaml', 'python-Levenshtein', 'docopt'],

    author="Felk",
    description="Tool for handling and processing Pokémon set data that is used for TPP matches.",
    url="https://github.com/TwitchPlaysPokemon/pokecat",
)
