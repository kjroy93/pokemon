"""class for darmanitan special case"""

# Dependencies
from bs4 import Tag

def darmanitan_types(location:Tag, gen:int):
    from backend.database.src.creature import Pokemon

    if gen < 8:
        strings = ['Normal','Zen Mode']
        darmanitan_types = Pokemon._get_elemental_types(Pokemon,strings,location)

        return darmanitan_types
    
    elif gen >= 8:
        strings = ['Normal','Zen Mode','Galarian']
        darmanitan_types = Pokemon._get_elemental_types(Pokemon,strings,location)
        darmanitan_types['Galarian Zen Mode'] = ['Ice','Fire']

        return darmanitan_types

def darmanitan_weakness(location:Tag, gen:int, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    if gen < 8:
        darmanitan = values[0:18]
        zen_mode = values[18:36]

        darmanitan_weakness = Pokemon._get_list_of_weakness(Pokemon,'darmanitan',None,elemental_types,darmanitan)
        zen_mode_weakness = Pokemon._get_list_of_weakness(Pokemon,'darmanitan',None,elemental_types,zen_mode)

        return darmanitan_weakness,zen_mode_weakness
    
    elif gen >= 8:
        darmanitan = values[0:18]
        galarian_darmanitan = values[18:36]
        zen_mode = values[36:54]
        galar_zen_mode = values[54:72]

        darmanitan_weakness = Pokemon._get_list_of_weakness(Pokemon,'darmanitan',None,elemental_types,darmanitan)
        galar_darmanitan_weakness = Pokemon._get_list_of_weakness(Pokemon,'darmanitan',None,elemental_types,galarian_darmanitan)
        zen_mode_weakness = Pokemon._get_list_of_weakness(Pokemon,'darmanitan',None,elemental_types,zen_mode)
        galar_zen_weakness = Pokemon._get_list_of_weakness(Pokemon,'darmanitan',None,elemental_types,galar_zen_mode)

        return darmanitan_weakness,galar_darmanitan_weakness,zen_mode_weakness,galar_zen_weakness