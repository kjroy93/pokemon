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

def eliminate_excess(positions:list[int], scrap:list[Tag | NavigableString]):
    return [element for idx, element in enumerate(scrap) if idx not in positions]

def is_physical_attack(table:List[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Physical', 'Other'])

def is_special_attack(table:List[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Special'])

def is_normal_form(table:List[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Normal'])

def is_regional_form(table:List[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean'])

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

def solve_img_tag(regional:bool=None):
    """
    Decorator that apply the same function, changing the string

    Parameter:
    - regional: boolean value that represent the result of another function, in order to know if the pokemon has a regional form.

    Returns:
    - A list containing Tags and NavigableString objects without the column that contain the string.

    Funtions:
    - decorator(func:Callable): This is what activates when you call the decorated function.
        - func: The decorated function.
        - Returns the result of the wraped function.
    - wrapper(line:List[Tag | NavigableString]=None, string:str=None, data_location:int=None, *args, **kwargs): The proper module/function/method that is being decored. in order to process the img problem of the web page Serebii.net of the module that is being decorated.
        - line: segment of the array that needs to be checked.
        - string: text that needs to be eliminated
        - data_location: first point in the line that is being checked.

    """

    def decorator(func:Callable):
        @wraps(func)
        def wrapper(line:List[Tag | NavigableString]=None, string:str=None, data_location:int=None, *args, **kwargs):
            """
            Proper function of the module/function/method that is being decored.
            - line: segment of the array that needs to be checked.
            - string: text that needs to be eliminated
            - data_location: first point in the line that is being checked.
            """

            # Fix the error in Serebii.net html, when it closes the tag of corresponding to regional form img with <img\> in the first element
            html = line[data_location]
            soup = BeautifulSoup(str(html), 'html.parser')

            if regional:
                img_tag = soup.find_all('img')
                if img_tag:
                    forms = [img.get('alt') for img in img_tag]
                    line[data_location] = forms[0]
                    line.insert(8,forms[1])

                result = func(line,string,*args,**kwargs)

                return result
            
            elif not regional:
                img_tag = soup.find('img')
                result = func(tag=img_tag,line=line,*args,**kwargs)

                return result
        
        return wrapper
    
    return decorator

def search_text(main_table:List[Tag], text:str):
    for table in main_table:
        if table[0].text == text:
            return table
        else:
            pass