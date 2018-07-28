
unowns = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!?"
burmy_wormadam = ["Plant", "Sandy", "Trash"]
deoxys = ["Normal", "Attack", "Defense", "Speed"]
shellos_gastrodon = ["West", "East"]
multitype_plates = {
    None: "Normal",
    "Meadow Plate": "Grass",
    "Flame Plate" : "Fire",
    "Splash Plate": "Water",
    "Sky Plate"   : "Flying",
    "Insect Plate": "Bug",
    "Toxic Plate" : "Poison",
    "Zap Plate"   : "Electric",
    "Mind Plate"  : "Psychic",
    "Stone Plate" : "Rock",
    "Earth Plate" : "Ground",
    "Dread Plate" : "Dark",
    "Spooky Plate": "Ghost",
    "Iron Plate"  : "Steel",
    "Fist Plate"  : "Fighting",
    "Icicle Plate": "Ice",
    "Draco Plate" : "Dragon",
    "Pixie Plate" : "Fairy",
}

multitype_colors = {
    None: "White",
    "Meadow Plate": "Green",
    "Flame Plate" : "Red",
    "Splash Plate": "Blue",
    "Sky Plate"   : "Blue",
    "Insect Plate": "Green",
    "Toxic Plate" : "Purple",
    "Zap Plate"   : "Yellow",
    "Mind Plate"  : "Pink",
    "Stone Plate" : "Yellow",
    "Earth Plate" : "Brown",
    "Dread Plate" : "Black",
    "Spooky Plate": "Purple",
    "Iron Plate"  : "Gray",
    "Fist Plate"  : "Brown",
    "Icicle Plate": "Blue",
    "Draco Plate" : "Purple",
    "Pixie Plate" : "Pink",
}

def get_multitype_type(plate):
    return multitype_plates.get(plate["name"], "Normal")

def get_multitype_color(plate):
    return multitype_plates.get(plate["name"], "White")

def get_formname(species, form):
    try:
        if species == 386: return deoxys[form]
        if species == 201: return unowns[form]
        if species in (412, 413): return burmy_wormadam[form]
        if species in (422, 423): return shellos_gastrodon[form]
    except IndexError:
        pass

def get_formnumber(species, formname):
    formname = formname.title()
    if species == 386: return deoxys.index(formname)
    if species == 201: return unowns.index(formname)
    if species in (412, 413): return burmy_wormadam.index(formname)
    if species in (422, 423): return shellos_gastrodon.index(formname)

