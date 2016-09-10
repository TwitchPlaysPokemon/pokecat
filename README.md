
**pokecat** is a tool meant for parsing and processing pokemon sets defined in the [TPPBR pokemon set definition format](pokesetspec.md). It is used for generating Pokémon that participate in matches played on [Twitch Plays Pokémon Battle Revolution](https://www.twitch.tv/twitchplayspokemon).

If you already want to test it, you can install and use *pokecat* as a command line tool:

```
$ python -m pokecat populate example.yaml example_populated.yaml
Seel Physical> Key should be all lowercase: Level
Seel Physical> Didn't recognize ability Thich Fat, but assumed Thick Fat.
Seel Physical> Didn't recognize item NeverMelt-Ice, but assumed NeverMeltIce.
Seel Physical> Didn't recognize ball Poke, but assumed Poké Ball.
Seel Physical> Set is shiny, but also biddable, which means it is not secret and usable in token matches at any time. Is this intended?
```

Correctable errors simply print warnings as you see. When the inputfile was successfully parsed, it produces the file [`example_populated.yaml`](example_populated.yaml). That file includes the same data, but populated to include all the optional fields and have things previously just identified by name or id be expanded into proper objects according to [this specification](unified_objects.md).

To instantiate a populated list of sets (reduce lists of options of e.g. multiple items or moves to one concrete object), use this command:

```
$ python -m pokecat instantiate example_populated.yaml example_instantiated.json
```

This command produces the file [`example_instantiated.json`](example_instantiated.json). Note that this command currently outputs the data in JSON-format instead of YAML. This is due to compatibility reasons with pbrEngine and might change in the future. 

To produce a list of completely random Pokésets, use the `genpokesets` command:

```
$ python -m pokecat genpokesets random_pokesets.yaml 6
```

This produces a file `random_pokesets.yaml` containing a list of 6 random Pokémon, structured the same as the output of `populate`.

To produce a list of completely random Pokémon, usually for testing, use the `genpokemon` command:

```
$ python -m pokecat genpokemon random_pokemon.json 6
```

This produces a file `random_pokemon.json` containing a list of 6 random Pokémon, structured the same as the output of `instantiate`.

All commands are also available as python functions:

```python
import pokecat
pokeset = {
    "species": "Bulbasaur",
    "setname": "Standard",
    "ability": "Sturdy",
    "nature":  "+atk -def",
    "ivs": 15,
    "evs": {"hp": 0, "atk": 0, "def": 252, "spe": 64, "spA": 32, "spD": 32},
    "moves": ["Ember", "Sheer Cold"]
}
populated      = pokecat.populate_pokeset(pokeset)
pokemon        = pokecat.instantiate_pokeset(populated)
print(pokemon)

random_pokeset = pokecat.generate_random_pokeset()
print(random_pokeset)

random_pokemon = pokecat.generate_random_pokemon()
print(random_pokemon)
```
