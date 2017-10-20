
import os

from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
__version__ = open(os.path.join(ROOT_DIR, 'VERSION')).read().strip()

setup(
    name="pokecat",
    version=__version__,
    packages=find_packages(),
    package_dir={"pokecat": "pokecat"},
    package_data={"pokecat": ["gen1data/*.json", "gen4data/*.json", "globaldata/*.json", "pbrdata/*.json"]},
    data_files=[("", ["VERSION"])],
    install_requires=['pyyaml', 'python-Levenshtein', 'docopt', 'unidecode'],

    author="Felk",
    description="Tool used by TwitchPlaysPokemon for handling and processing Pokémon set data, metasets, and some global utilities.",
    url="https://github.com/TwitchPlaysPokemon/pokecat",
)
