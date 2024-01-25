"class for tauros special case"

# Dependencies
from bs4 import Tag

def tauros_types(location:Tag):
    from backend.database.src.src import Pokemon

    strings = ['Normal','Paldean']

    tauros = Pokemon._get_elemental_types(Pokemon,strings,location)

    race = ['Blaze Breed','Aqua Breed']

    tauros_special = Pokemon._get_elemental_types(Pokemon,race,location)

    tauros.update(tauros_special)

    return tauros