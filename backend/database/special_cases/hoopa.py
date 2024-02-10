"""class for hoopa special case"""

# Dependencies
from bs4 import Tag

def hoopa_types(location:Tag):
    from backend.database.src.creature import Pokemon
    
    hoopas = location.text.strip().split()
    hoopa_form = [f'{hoopas[i]} {hoopas[i + 1]}' for i in range(0,len(hoopas),2)]

    hoopa_types = Pokemon._get_elemental_types('hoopa',hoopa_form,location)

    return hoopa_types

def hoopa_weakness(location:Tag, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    hoopa_confined = values[0:18]
    hoopa_unbound = values[18:36]

    hoopa_c_weakness = Pokemon._get_list_of_weakness(Pokemon,'hoopa',None,elemental_types,hoopa_confined)
    hoopa_u_weakness = Pokemon._get_list_of_weakness(Pokemon,'hoopa',None,elemental_types,hoopa_unbound)

    return hoopa_c_weakness,hoopa_u_weakness