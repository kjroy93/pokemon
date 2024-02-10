"""class for zacian/zamazenta special case"""

# Dependencies
from bs4 import Tag
from typing import Type

def heroes_types(location:Tag, name:Type[object]):
    from backend.database.src.creature import Pokemon
    strings = ['Hero of Many Battles', 'Crowned Sword', 'Crowned Shield']

    if 'Zacian' in name:
        forms = [strings[0],strings[1]]
    elif 'Zamazenta' in name:
        forms = [strings[0],strings[2]]
    
    hero = Pokemon._get_elemental_types(Pokemon,forms,location)

    return hero

def heroes_weakness(location:Tag, elemental_types:list) -> tuple[dict | list]:
    from backend.database.src.creature import Pokemon

    values = location[18:]
    hero = values[0:18]
    crowned = values[18:36]

    hero_weakness = Pokemon._get_list_of_weakness(Pokemon,'heroes',None,elemental_types,hero)
    crowned_weakness = Pokemon._get_list_of_weakness(Pokemon,'heroes',None,elemental_types,crowned)
    
    return hero_weakness,crowned_weakness