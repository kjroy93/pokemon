# Special Functions in order for main class more legible

from typing import Literal
from bs4 import Tag,ResultSet

def find_table_by_class(gen:int, main_table:ResultSet, class_name:str, normal_form:str=None, index:int=0) -> ResultSet:
    """
    Function that goes to the exact class that contains the information, with the information that recives from self.__basic_tables() method in Pokémon class:

    Requirements:

    - gen: Generation.
    - main_table: This is BeautifulSoup HTML.text parser that contains all the information.
    - class_name: The class that needs to be located in the HTML.
    - normal_form: WARNING! This only applies if the Pokémon contains a Mega Evolution. This value comes preloaded from the Mega Pokemon class.\n
    The flag cames with None from default, so it does not need change.
    - index: Proper location of the table. Do not give any value, unless you know what you are doing, in the main center distribution of the webpage.
    
    """
    match normal_form:
        case None:
            if gen != 8:
                return main_table[index].find_all('td', {'class': class_name})
            else:
                return main_table[index + 1].find_all('td', {'class': class_name})
            
        case 'form':
            if gen != 8:
                return main_table[index].find_all('table', {'class': 'dextable'})

def get_elemental_types(location:Tag, info:Literal['weakness'], form:str=None, elements:list=None) -> list:
    match form:
        case None:
            types = []
            if info == 'weakness':
                location = location[0:18]

            for tag in location:
                a_tag = tag.find('img')
                if a_tag and not isinstance(a_tag,Tag):
                    continue
                else:
                    print(f'aqui se busca el tipo {a_tag}')
                    type_text = a_tag['alt']
                    types.append(type_text)

            s = 'Attacking Move Type: ','-type'
            for string in s:
                types = list(map(lambda x: x.replace(string,''),types))
            
            return types
        
        case form:
            types = []
            for tag in location:
                a_tag = tag.find('img')
                if a_tag and not isinstance(a_tag,Tag):
                    continue
                else:
                    type_text = a_tag['src']

                for element in elements:
                    ty = element.lower()
                    if ty in a_tag:
                        types.append(element)
            
            return types

def get_parents(parents:list) -> dict:
    pokemon_groups = {}
    current_group = parents[0]
    pokemon_groups[current_group] = []

    for parent in parents[1:]:
        pokemon_groups[current_group].append(parent)
    
    return pokemon_groups

def process_hidden_ability(tag:Tag, abilities_dict:dict, form_abilities_dict:dict, skip_next_flag:bool, form_abilities_flag:bool) -> bool:
    next_tag = tag.find_next('b')
    if next_tag:
        ability = next_tag.text
        ability_text = next_tag.next_element.next.strip()
        to_join = [ability, ability_text]
        result = ''.join(to_join)

        if form_abilities_flag:
            form_abilities_dict['hidden_ability'].append(result)
        else:
            abilities_dict['hidden_ability'].append(result)

        skip_next_flag = True

    return skip_next_flag

def process_ability(tag:Tag, abilities_dict:dict, form_abilities_dict:dict, form_abilities_flag:bool):
    father = tag
    ability = father.text
    ability_text = father.next_element.next.strip()
    to_join = [ability, ability_text]
    result = ''.join(to_join)

    if 'Form' in father.text:
        result = ''
    
    if result != '' and form_abilities_flag:
        form_abilities_dict['ability'].append(result)
    elif result != '':
        abilities_dict['ability'].append(result)

def process_form_ability(tag:Tag, form_abilities_flag:bool):
    father = tag.text
    if 'Form' in father:
        form_abilities_flag = True
    return form_abilities_flag

def stats_calculation(stat:str, base:int, EV:int=0, level:int=50, nature=1, IV=31):
    if stat == 'hp':
        hp = ((IV+2*base+(EV/4))*level/100)+10+level
        return hp
    else:
        st = (((IV + 2 * base + (EV/4) ) * level/100 ) + 5) * nature
        return st

def detect_new_forms(pokemon_name:str, main_table:ResultSet) -> (int|str):
    #Get al tables from the main center table
    tables = main_table[0].find_all('table', {'class': 'dextable'})

    #Search for the line that contains <td class="fooevo" colspan="6">
    for i, table in enumerate(tables):
        if table.find('td', {'class': 'fooevo', 'colspan': '6'}):
            return i
    
    return f'{pokemon_name} does not have Mega'