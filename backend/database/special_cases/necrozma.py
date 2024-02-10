"class for necrozma special case"

# Dependencies
from bs4 import Tag

def necrozma_types(location:Tag):
    from backend.database.src.creature import Pokemon

    necrozma = location.text.strip().replace('Normal','Normal ').split()
    forms = necrozma[1:5]

    necrozma_forms = [f'{forms[i]} {forms[i+1]}' for i in range(0,len(forms),2)]
    necrozma_forms = ['Normal'] + necrozma_forms

    necrozma_types = Pokemon._get_elemental_types(Pokemon,necrozma_forms,location)

    return necrozma_types

def necrozma_weakness(location:Tag, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    normal = values[0:18]
    dusk = values[18:36]
    dawn = values[36:54]

    necrozma_n_weakness = Pokemon._get_list_of_weakness(Pokemon,'necrozma',None,elemental_types,normal)
    necrozma_dusk_weakness = Pokemon._get_list_of_weakness(Pokemon,'necrozma',None,elemental_types,dusk)
    necrozma_dawn_weakness = Pokemon._get_list_of_weakness(Pokemon,'necrozma',None,elemental_types,dawn)

    return necrozma_n_weakness,necrozma_dusk_weakness,necrozma_dawn_weakness