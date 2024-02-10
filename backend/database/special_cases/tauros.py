"class for tauros special case"

# Dependencies
from bs4 import Tag

def tauros_types(location:Tag):
    from backend.database.src.creature import Pokemon

    strings = ['Normal','Paldean']

    tauros = Pokemon._get_elemental_types(Pokemon,strings,location)

    race = ['Blaze Breed','Aqua Breed']

    tauros_special = Pokemon._get_elemental_types(Pokemon,race,location)

    tauros.update(tauros_special)

    return tauros

def tauros_weakness(location:Tag, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    tauros = values[0:18]
    paldean_tauros = values[18:36]
    blaze_tauros = values[36:54]
    aqua_tauros = values[54:72]

    tauros_weakness = Pokemon._get_list_of_weakness(Pokemon,'tauros',None,elemental_types,tauros)
    paldean_tauros_weakness = Pokemon._get_list_of_weakness(Pokemon,'tauros',None,elemental_types,paldean_tauros)
    blaze_tauros_weakness = Pokemon._get_list_of_weakness(Pokemon,'tauros',None,elemental_types,blaze_tauros)
    aqua_tauros_weakness = Pokemon._get_list_of_weakness(Pokemon,'tauros',None,elemental_types,aqua_tauros)

    return tauros_weakness,paldean_tauros_weakness,blaze_tauros_weakness,aqua_tauros_weakness