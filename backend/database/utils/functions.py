# Standard libraries of Python
from functools import wraps
from typing import List, Callable

# Dependencies
from bs4 import BeautifulSoup, Tag, ResultSet, NavigableString

def number_generator(init:int):
    for number in range(init,1000):
        yield number
    
def remove_string(data:List[str]):
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

def is_physical_attack(table:List[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Physical', 'Other'])

def is_special_attack(table:List[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Special'])

def is_normal_form(table:List[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Normal'])

def is_regional_form(table:List[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean'])

def egg_move_regional_form():
    """
    Decorator that apply the same function, changing the string

    Returns:
    - A list containing Tags and NavigableString objects without the column that contain the string.

    Funtions:
    - decorator(): This is what activates when you call the decorated function.
        - func: The decorated function.
        - The result of the wraped function.

    - wrapper: The proper function of the module that is being decorated.
        - to_fix: Line to be cleaned.
        - The result of the decorated function.

    """

    def decorator(func:Callable):
        @wraps(func)
        def wrapper(to_fix:List[Tag], string:str, data_location:int, *args, **kwargs):
            # Fix the error in Serebii.net html, when it closes the tag of corresponding to regional form img with <img\> in the first element
            html = to_fix[data_location]
            soup = BeautifulSoup(str(html), 'html.parser')

            img_tag = soup.find_all('img')
            if img_tag:
                forms = [img.get('alt') for img in img_tag]
                to_fix[7] = forms[0] # Change the original img table with the normal form Pokémon
                to_fix.insert(8, forms[1]) # Add the regional form Pokémon
            
            result = func(to_fix,string,*args,**kwargs)

            return result
        
        return wrapper
    
    return decorator

def search_text(main_table:List[Tag], text:str):
    for table in main_table:
        if table[0].text == text:
            return table
        else:
            pass