# Special Functions in order for main class to be more readable
import re
from typing import Literal
from bs4 import Tag,ResultSet

def find_table_by_class(gen:int, main_table:ResultSet, class_name:str, normal_form:str=None, index:int=0) -> ResultSet:
    """
    Function that goes to the exact class that contains the information, with the information that recives from self.__basic_tables() method in Pokémon class:

    Requirements:

    - gen: Generation.
    - main_table: This is BeautifulSoup HTML.text parser that contains all the information.
    - class_name: The class that needs to be located in the HTML.
    - normal_form: WARNING! This only applies if the Pokémon contains a Mega Evolution. This value comes preloaded from the Mega Pokemon class.
    The flag cames with None from default, so it does not need change.
    - index: Proper location of the table. Do not give any value, unless you know what you are doing, in the main center distribution of the webpage.
    
    """
    match normal_form:
        case None:
            if gen < 8:
                return main_table[index].find_all('td', {'class': class_name})
            elif gen >= 8:
                return main_table[index + 1].find_all('td', {'class': class_name})
            
        case 'form':
            if gen < 8:
                return main_table[index].find_all('table', {'class': 'dextable'})
            else:
                raise ValueError("Error. Parameter with no posible resolve")

def find_word(tag):
    text = tag.name == 'td' and 'Form' in tag.text
    text_1 = tag.name == 'td' and 'Standard' in tag.text

    if text:
        return text
    else:
        return text_1

def find_atribute(location):
    return location.br.next_sibling.text.split('\r\n\t\t\t').pop(1)

def remove_string(data: list):
    s = 'Attacking Move Type: ','-type'
    for string in s:
        data = list(map(lambda x: x.replace(string,''),data))

    return data

def list_of_elements(location:Tag):
    types = []
    location = location[0:18]

    for tag in location:
        a_tag = tag.find('img')
        if a_tag and not isinstance(a_tag,Tag):
            continue

        else:
            type_text = a_tag['alt']
            types.append(type_text)
    
    types = remove_string(types)
    
    return types

def elemental_types(location:Tag, form:Literal['mega']=None, elements:list=None) -> list:
    match form:
        case None:
            base_form = []
            regional_form = []

            if location.find(string='Normal'):
                main = location.find_all('td')

                for index,tag in enumerate(main):
                    lazy = tag.text.strip()

                    if 'Normal' in lazy:
                        basic = main[index+1].find('img')
                        type_text = basic['alt']
                        base_form.append(type_text)
                    elif lazy:
                        basic = main[index+1].find_all('img')
                        for e in basic:
                            type_text = e['alt']
                            regional_form.append(type_text)
                
                base_form = remove_string(base_form)
                regional_form = remove_string(regional_form)

                return {'normal': base_form, 'regional': regional_form}
            
            else:
                types = []
                for tag in location:
                    a_tag = tag.find('img')
                    if a_tag and not isinstance(a_tag,Tag):
                        continue
                    else:
                        type_text = a_tag['alt']
                        types.append(type_text)
                types = remove_string(types)
                
                return types
        
        case 'mega':
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

def filter_types(locations:list):
    elements = [tag.text for tag in locations if '*' in tag.get_text(strip=True)]
    v = list(map(lambda x: x.replace('*',''),elements))

    return v

def form_standard_case(main:ResultSet,word:str) -> list:

    result_set = main.find_all('td')

    normal = []
    regional = []

    regex_patern = fr'\d+\.\d+{word}'

    lazy = result_set[0].text.strip()

    if 'Form' in lazy:
        for index,_ in enumerate(result_set):

            match = re.search(regex_patern, result_set[index+2].text)
            
            if match:
                data = match.group()
                if index % 2 == 0:
                    normal.append(data)
                else:
                    regional.append(data)
                
                if normal and regional:
                    break
        
        return normal,regional

    elif 'Standard' in lazy:
        match = re.search(regex_patern, result_set[index+1].text)

        if match:
            data = match.group()
            normal.append(data)
        
        return normal

def get_filters(location:list):
    normal_val = filter_types(location[18:36])
    regional_val = filter_types(location[36:55])

    return normal_val,regional_val

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
        hp = ((IV + 2 * base + (EV / 4)) * level / 100) + 10 + level
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