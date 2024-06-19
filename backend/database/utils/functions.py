# Standard libraries of Python
from functools import wraps
from typing import Callable

# Dependencies
from bs4 import BeautifulSoup, Tag, ResultSet, NavigableString

def number_generator(init:int):
    for number in range(init,1000):
        yield number
    
def remove_string(data:list[str]):
    words = 'Attacking Move Type: ','-type'
    for string in words:
        data = list(map(lambda x: x.replace(string,''),data))

    return data

def make_dict(elemental:list, v:list):
    return dict(zip(elemental,v))

def eliminate_excess(positions:list[int], scrap:list[Tag | NavigableString]):
    return [element for idx, element in enumerate(scrap) if idx not in positions]

def empty_category_fix(to_fix:list[Tag | NavigableString]=None, index:int=None):
    if index == 2:
        to_fix.insert(index, 'Other')
        to_fix.insert(index+1, 'N/A')
        to_fix.insert(index+2, '--')
    else:
        to_fix.insert(index, 'N/A')

def normal_regional(pokemon_ability:dict | list):
    if isinstance(pokemon_ability,dict):
        k = pokemon_ability.keys()
        return True if any([i in ['Alolan','Galarian','Hisuian','Paldean'] for i in k]) else False
    elif isinstance(pokemon_ability,list):
        return False

def regional_case(numerator:int, scrap:list[Tag]):
    last_element = 11
    if hasattr(scrap[numerator+9],'get'):
        return last_element if numerator == 0 or isinstance(scrap[numerator+9].get('alt',''),str) else 10
    else:
        return last_element - 1

def regional_z_max(numerator:int, scrap:list[Tag]):
    last_element = 11
    if hasattr(scrap[numerator+3],'get'):
        return last_element if numerator == 0 or isinstance(scrap[numerator+8].get('alt',''),str) else 10
    else:
        return (10 if any(
                word in scrap[numerator+7].get('alt','')
                for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean', 'Normal'] if not isinstance(
                    scrap[numerator+7], NavigableString
                )
            ) and hasattr(scrap[numerator+8], 'get') else 9
        ) if len(scrap) - numerator > 9 else 8

def elements_atk(a_tag:Tag, control:int=None):
    elemental_types = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
        'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
    ]

    category = [
        'physical', 'special', 'other'
    ]

    minus = [elemental_type.lower() for elemental_type in elemental_types]

    if control == None:
        text = minus
    elif control == 1:
        text = category
    else:
        raise ValueError('The Control variable must be 1 if you want to process atk types')

    for n,i in enumerate(text):
        type_text = a_tag['src']
        if i in type_text:
            return str(text[n].capitalize())

def list_of_elements(location:ResultSet[Tag]):
    types = []
    location = location[0:18]

    for tag in location:
        a_tag = tag.find('img')
        if a_tag and not isinstance(a_tag,Tag):
            continue

        try:
            type_text = a_tag['alt']
            types.append(type_text)
        except KeyError:
            type_text = elements_atk(a_tag)
            types.append(type_text)
    
    types = remove_string(types)
    
    return types

def search_text(main_table:list[Tag], text:str):
    for table in main_table:
        if table[0].text == text:
            return table
        else:
            pass