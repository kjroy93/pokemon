# Standard libraries of Python

# Dependencies
from bs4 import Tag

# Libraries

def number_generator(init:int):
    for number in range(init,1000):
        yield number
    
def remove_string(data:list):
    s = 'Attacking Move Type: ','-type'
    for string in s:
        data = list(map(lambda x: x.replace(string,''),data))

    return data

def make_dict(elemental:list, v:list):
    return dict(zip(elemental,v))

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

def list_of_elements(location:Tag):
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

def is_physical_attack(table:list[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Physical', 'Other'])

def is_special_attack(table:list[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Special'])

def is_normal_form(table:list[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Normal'])

def is_regional_form(table:list[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean'])