
# TPPBR Pokémon set definition format specification

This document specifies the format in which Pokémon sets are defined for Twitch Plays Pokémon Battle Revolution. It is a YAML compliant format tailored to fit the needs of people maintaining the sets. Moreover, this document describes how a program parsing the file format should behave.

## Requirements

The format must be easily understandable and usable by people not adept in programming or similar technical tasks. This implies error tolerance against common mistakes such as: 
- additional whitespace
- spelling errors
- wrong case-sensitivity
If the data is unambiguous and valid, it should still get accepted, but trigger a warning message. If the data is ambiguous, invalid, or the errors would require too much programming work to auto-fix, the parser should reject the data with proper error messages and require it to be fixed.

It must be possible to hint a set's chance to be chosen, in order to be able to define more and lesser rare sets.

## Structure

The data format used is [`YAML`](http://yaml.org/spec/1.1/), which mainly consists of key-value mappings. The order in which they appear is irrelevant, but it should be consistent to keep it readable. Full knowledge of YAML is not needed to be able to edit Pokémon sets, as it is very simple and can be learned by just copying from existing sets. Here's an example of a minimal Pokémon set:

```
ingamename: ARCEUS-FIR
species: Arceus
setname: Standard
item: Flame Plate
ability: Multitype
nature: Modest
ivs: 0
evs: {hp: 0, atk: 0, def: 0, spe: 64, spA: 32, spD: 32}
moves:
    - Ember
    - Gastro Acid
    - Haze
    - Sunny Day
```

Here's an example of a Pokémon set with all features being used:

```
ingamename: SEEL-PH
species: Seel
setname: Physical
item: [Rawst Berry, Toxic Orb, Light Ball, NeverMelt-Ice]
ability: [Thick Fat, Hydration]
nature: Adamant
ivs: 31
evs: {hp: 8, atk: 252, def: 120, spA: 0, spD: 120, spe: 8}
moves:
    - Fake Out
    - [Aqua Tail, Dive, Waterfall]
    - [Double-Edge, Facade, Body Slam, Fling, Toxic]
    - [Horn Drill, Aqua Jet, Ice Shard]
combinations:
    - [Toxic Orb, Facade]
    - [Light Ball, Fling]
    - [NeverMelt-Ice, Ice Shard]
    - [Dive, Toxic]
separations:
    - [Aqua Tail, Fling]
    - [Aqua Tail, Body Slam]
gender: [m, f]
form: 0
happiness: 255
shiny: True
biddable: True
rarity: 0.1
ball: [Poké, Master]
level: 100
```

Empty lines have no meaning. Start lines with `#` to add a comment and use 3 dashes `---` to separate multiple sets within a file.

## Possible fields

All Pokémon, items and abilities must be from 4th generation or earlier, because PBR is a 4th generation game. Also the combination of species and setname must be unique.

### Obligatory fields

**setname**
  : Defaults to "Standard". The name of the current set. Should be used to differentiate multiple sets of the same species, e.g. "Stadium 2", "Physical" or "High Attack". Should *not* be used to name formes like "A" as in Unown A or "Psychic" as in Arceus Psychic, as the form names get automatically added.

**species**
  : The Pokémon species. Can either be a Pokémon name or a National Pokédex number.
  
**ability**
  : The Pokémon's ability. Can either be an ability name or an abiliy number. Can also be a *list of abilities* (e.g. `[Blaze, Solar Power]`) to let RNG decide.
  
**nature**
  : The Pokémon's nature. Can either be a nature name, a nature number (0 = Hardy, 24 = Quirky) or a nature defined by boosted and nerfed stat (for example `+atk -spD`)
  
**ivs**
  : The Pokémon's Individual Values. Can either be a single number (e.g. `0`) to be the same for all stats, or a dictionary containing a value for each stat (`hp`, `atk`, `def`, `spe`, `spA` and `spD`).
  : *Note:* An inline dictionary consists of comma-separated `key:value` pairs enclosed in curly braces, like in the example.
  
**evs**
  : Same as *IVs*, but for Effort Values. The sum of all values cannot exceed 510, and one single stat cannot have more than 252 EVs.

**moves**
  : The Pokémon's moves. Must contain a list of moves. Each move can either be a movename, a move number or a  *list of moves* to let RNG decide. Each move can additionally be followed by a number of `n` PP ups in the format `(+n)` and `m` fixed PP in the form of `(=m)`, or even both in the form `(+n/=m)`. For example `Detect (=1)`

### Optional fields

**ingamename**
  : Name the Pokémon has ingame. Defaults to the Species' name in uppercase, ending in `-S` if shiny. Maximum of 10 characters, therefore the default might have a shortened species name (e.g. `TYPHLOSI-S` for shiny Typhlosion). Can only contain ASCII characters and the male/female sign. While not necessarily unique, Pokémon with the same ingame name cannot be in the same match due to technical limitations.

**gender**
  : Defaults to null (no gender). Can also be "m" and "f", or a *list of genders* (e.g. `[m, w]`) to let RNG decide.
  : *Note:* Mixing male and female with no gender in the same species can crash PBR. For each species (therefore also across all set for that species) agree on sticking to whether that species is genderless or not.

**form**
  : Defaults to `0`. Can be a form number, or a form name specific to a given Pokémon. The following form names are valid:
    - Unown: A-Z, ? and !
    - Burmy and Wormadam: Plant, Sandy, Trash
    - Deoxys: Attack, Defense, Speed
    - Shellos and Gastrodon: West and East

**item**
  : Defaults to `null` (no item). The Pokémon's held item. Can either be an item name or an item number. Can also be a *list of items* (e.g. `[Chesto Berry, Poison Barb]`) to let RNG decide.

**displayname**
  : *Recommended not to use*. Defaults to the species' name modified to include eventual form names. For example:
    - Deoxys in attack form would get the display name "Deoxys Attack"
    - Unown in A-Form would get the display name "Unown A"
    - Arceus with the Multitype-ability the item Flame Plate (although not technically a form) would get the display name "Arceus Fire"

**happiness**
  : Defaults to 255. The Pokémon's Friendship Value. Is used to determine the base power of the moves "Return" and "Frustration".

**shiny**
  : Defaults to `false`. If `true`, the Pokémon is shiny.

**biddable**
  : Defaults to `true`, except for Pokémon with `shiny` set to `true`, where it defaults to `false`. If `false`, the Pokémon is not available for token match bidding. It will be treated as non-existent, conceiling its existence to not spoil new shinies for example.

**rarity**
  : Defaults to `1.0`. Multiplier for the chance this set gets chosen by RNG. Values smaller than `1.0` cause this set to be selected less often. Values greater than `1.0` cause this set to be selected more often. For example `2.0` doubles this set's chance to get picked.
  : `0` means RNG will never choose this set. Can be used for token-bid-only sets.

**ball**
  : Defaults to "Poké". Sets the ball the Pokémon is caught with. Can be any ball type's name, for example "Master". Can also be a *list of ballnames* (e.g. `[Poké, Ultra]`) to let RNG decide.

**level**
  : Defaults to `100`. The level of the Pokémon. Can be between 1 and 100.

**combinations**
  : Defaults to empty list. List of groups (also lists) of moves, items and/or abilities that *have* to appear together and therefore cannot be chosen by RNG without all the others also being chosen. See the example of a full Pokémon set for a usecase.

**separations**
  : Defaults to empty list. List of groups (also lists) of moves, items and/or abilities that *must not* appear together and therefore cannot be chosen by RNG while any of the others are also chosen. See the example of a full Pokémon set for a usecase.
