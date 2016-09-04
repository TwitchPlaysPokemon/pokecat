
# Standardized data objects for Twitch Plays Pokémon

This document specifies how various data objects should be structured and named, mainly accross Twitch Plays Pokémon applications. It is not meant to be a complete standard, but rather fulfill the needs of TPP. Therefore the available fields are stripped down to only include the most used fields. Its goal is to standardize those conventions to enable Pokémon data to be submitted cross-application. The structures are defined in commented JSON. If this standard is insufficient for you, try orienting yourself after the names [Smogon](http://www.smogon.com/) or [pokeapi.co](http://pokeapi.co/) uses.

Which fields are optional and which arent is to be decided by the application utilizing this standard. There also is no localization, everything is in english.

## Species

A `Species` object describes a Pokémon species. This object is deliberately not called just `Pokemon` as that name is too generic and can mean different things depending on the context.

```
{
    "id": 1,                      # National Pokédex number of that Pokémon
    "name": "Bulbasaur",          # english name of the species
    "basestats": [Stats object],  # base stats of that species
    "types": [Type objects ...]   # base types of that species, length 1 or 2
}
```

## Stats

A `Stats` object uses the standardized 3-letter abbreviations, lowercase except for `spA` and `spD`. If the stats need to have an order/indices, the preferred order is `hp atk def spA spD spe`.

```
{
    "hp": 45,   # number, value of that stat
    "atk": 49,  # number, value of that stat
    "def": 49,  # number, value of that stat
    "spA": 65,  # number, value of that stat
    "spD": 65,  # number, value of that stat
    "spe": 45   # number, value of that stat
}
```

If using the 3-letter abbreviations is not an option, the preferred alternative is `hp attack defense special_attack special_defense speed`. Note how `hp` is not un-abbreviated, as its meaning is ambiguous ("hit points" or "health points"). "hp" is a word now.

## Type

A `Type` is defined as a title-cased string. A type can be one of these values:

```
[
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy",
    "???"  # Might need special treatment
]
```

If indices are needed, use the list above.

## Ability

Data for `Ability` objects may vary between different generations and/or games.

```
{
    "id": 1,                 # ID of that ability, same as game-internal ID
    "name": "Stench",        # english name of that ability
    "description": "<snip>"  # description of that ability. Could be any text.
}
```

## Item

Data for `Item` objects may vary between different generations and/or games.

```
{
    "id": 1,                 # ID of that item, same as game-internal ID
    "name": "Master Ball",   # english name of that item
    "description": "<snip>"  # description of that item. Could be any text.
}
```

## Nature

```
{
    "id": 1,                 # ID of that nature, same as game-internal ID (0=Hardy, 24=Quirky)
    "name": "Lonely",        # english name of that ability
    "increased": "atk",      # name of the stat increased by that ability
    "decreased": "def",      # name of the stat decreased by that ability
    "description": "<snip>"  # description of that nature. Could be any text.
}
```

## Move

Data for `Move` objects may vary between different generations and/or games. 

```
{
    "id": 1,             # ID of that move, same as game-internal ID
    "name_id": "pound",  # simplyfied string-representation of that move*
    "category": [Category object],  # category of that move. Can be "Physical", "Special" and "Status"
    "type": [Type object],          # type of that move 
    "accuracy": 100,     # base accuracy of that move. between 0 and 100, and can also be null (no accuracy)
    "name": "Pound",     # english name of that move
    "power": 40,         # base power of that move, minimum 0
    "pp": 35,            # PP of that move
    "pp_ups": 0          # number of PP-ups (20% pp increases) that move has**
}
```

*) The `name_id` field is the move's name stripped down to lowercase, alphanumeric characters. For example `Fire Punch` becomes `firepunch` and `Double-Edge` becomes `doubleedge`. This is to counter subtle changes in spelling between generations, but still have a readable identifier.

**) the `pp_ups` field should only be used if the `Move` object is used as a concrete move a Pokémon has. In this case the `pp` field should already include the extra pp gained through the amount of `pp_ups`

## Category (for moves)

A `Category` is defined as a title-cased string. A category can be one of these values:

```
[
    "Physical",
    "Special",
    "Status"
]
```

If indices are needed, use the list above.

## Gender

A `Gender` is defined as a single-character string. A gender can either be `"m"` or `"f"`. The preferred representation for "no gender" is `null`. If that isn't an option, the preferred alternative is `"-"`.


