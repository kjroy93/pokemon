"""class for calyrex special case"""

# Dependencies
from bs4 import Tag

def calyrex_types(location:Tag):
    from backend.database.src.creature import Pokemon

    text = location.text.strip().split()
    forms = [f'{text[i]} {text[i+1]}' for i in range(1,len(text),2)]
    calyrex_t = text.pop(0)
    calyrex = [calyrex_t] + forms

    calyrex_types = Pokemon._get_elemental_types(Pokemon,calyrex,location,'calyrex')

    return calyrex_types

def calyrex_weakness(location:Tag, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    calyrex = values[0:18]
    calyrex_ice = values[18:36]
    calyrex_shadow = values[36:54]

    calyrex_weakness = Pokemon._get_list_of_weakness(Pokemon,'calyrex',None,elemental_types,calyrex)
    calyrex_i_weakness = Pokemon._get_list_of_weakness(Pokemon,'calyrex',None,elemental_types,calyrex_ice)
    calyrex_s_weakness = Pokemon._get_list_of_weakness(Pokemon,'calyrex',None,elemental_types,calyrex_shadow)

    return calyrex_weakness,calyrex_i_weakness,calyrex_s_weakness