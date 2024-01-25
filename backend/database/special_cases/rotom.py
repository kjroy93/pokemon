# Dependencies
from bs4 import Tag


def rotom_types(location:Tag):
    from backend.database.src.src import Pokemon

    rotoms = location.text.split()
    rotoms.pop(5)
    rotom_forms = [variant[5:] + ' ' + 'Rotom' for variant in rotoms]
    rotoms = ['Rotom'] + rotom_forms

    rotoms_type = Pokemon._get_elemental_types(Pokemon,rotoms,location)

    return rotoms_type

def rotom_weakness(location:Tag, elemental_types:list):
    from backend.database.src.src import Pokemon

    values = location[18:]

    rotom = values[0:18]
    heat_rotom = values[18:36]
    wash_rotom = values[36:54]
    frost_rotom = values[54:72]
    fan_rotom = values[72:90]
    mow_rotom = values[90:108]

    r_weakness = Pokemon._get_list_of_weakness(Pokemon,'rotom',None,elemental_types,rotom)
    hr_weakness = Pokemon._get_list_of_weakness(Pokemon,'rotom',None,elemental_types,heat_rotom)
    wr_weakness = Pokemon._get_list_of_weakness(Pokemon,'rotom',None,elemental_types,wash_rotom)
    fr_weakness = Pokemon._get_list_of_weakness(Pokemon,'rotom',None,elemental_types,frost_rotom)
    fanr_wekaness = Pokemon._get_list_of_weakness(Pokemon,'rotom',None,elemental_types,fan_rotom)
    mr_weakness = Pokemon._get_list_of_weakness(Pokemon,'rotom',None,elemental_types,mow_rotom)

    return r_weakness,hr_weakness,wr_weakness,fr_weakness,fanr_wekaness,mr_weakness