
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

Correctable errors simply print warnings as you see. When the inputfile was successfully parsed, it produces the file `example_populated.yaml`. That file includes the same data, but populated to include all the optional fields and have things previously just identified by name or id be expanded into proper objects (like moves).
