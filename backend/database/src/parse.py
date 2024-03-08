# Special Functions in order for main class to be more readable
import re
from typing import Literal
from bs4 import Tag, ResultSet, NavigableString

from backend.database.utils import functions

def find_table_by_class(gen:int, main_table:ResultSet, class_name:str=None, search:Literal['form','moveset']=None) -> ResultSet:
    """
    Function that goes to the exact class that contains the information, with the information that recives from self.__basic_tables() method in Pokémon class:

    Attributes:

    - gen: Generation.
    - main_table: This is BeautifulSoup HTML.text r that contains all the information.
    - class_name: The class that needs to be located in the HTML. If there is a None in the Mega evolution class, is because the class_name does not matter in that case. Check the method in Mega_Pokemon.
    - search: WARNING! This only applies if you don´t need any class_name. If it´s None, it means that you want a class_name, not a table pre-constructed in this function.
        - This applies in the following cases:
        - Mega Pokemon.
        - moveset
    """
    match search:
        case None:
            if gen < 8:
                return main_table[0].find_all('td', {'class': class_name})
            elif gen >= 8:
                return main_table[1].find_all('td', {'class': class_name})
            
        case 'form':
            if gen < 8:
                return main_table[0].find_all('table', {'class': 'dextable'})
            else:
                raise ValueError("Error: Parameter with no possible resolution, because Mega Evolutions are not available in 8th Generation and onward")
        
        case 'moveset':
            if gen < 8:
                table = main_table[0].find_all('table', {'class': 'dextable'})
                return table
            elif gen >= 8:
                table = main_table[1].find_all('table', {'class': 'dextable'})
                return table

def find_word(tag):
    text = tag.name == 'td' and 'Form' in tag.text
    text_1 = tag.name == 'td' and 'Standard' in tag.text

    if text:
        return text
    else:
        return text_1

def find_atribute(location):
    return location.br.next_sibling.text.split('\r\n\t\t\t').pop(1)

def filter_types(locations:list):
    elements = [tag.text for tag in locations if '*' in tag.get_text(strip=True)]
    v_int = list(map(lambda x: x.replace('*',''),elements))

    return v_int

def get_filters(location:list, control:int=0):
    if control == 0:
        types_values = filter_types(location[18:36])

        return types_values
    
    elif control == 1:
        normal_val = filter_types(location[18:36])
        regional_val = filter_types(location[36:54])
        
        return normal_val,regional_val

def n_columns(number:int, moves:Literal['lv']=None):
    match number:
        case 9:
            c_names = [
                'level' if moves == 'lv' else 'tm_hm',
                'atk_name',
                'type',
                'category',
                'power',
                'accuracy',
                'pp',
                'effect',
                'description'
            ]

            return c_names
        
        case _:
            c_names = [
                'atk_name',
                'type',
                'category',
                'power',
                'accuracy',
                'pp',
                'effect',
                'description'
            ]

            return c_names

def columns_data_type(quantity_of_columns,reshape,egg_moves,moves):
    if quantity_of_columns == 9:
        for i in reshape:
            if moves == None:
                i[0] = i[0].text
            
            i[1] = i[1].text
            i[2] = functions.elements_atk(i[2])
            i[3] = functions.elements_atk(i[3],1)

    elif quantity_of_columns == 8:
        for i in reshape:
            if egg_moves == 'yes':
                del i[7]

            i[0] = i[0].text
            i[1] = functions.elements_atk(i[1])
            i[2] = functions.elements_atk(i[2],1)

def elemental_types(location:Tag, form:Literal['mega']=None, elements:list=None, pokemon:str=None):
    forms = ['Alolan','Galarian','Hisuian','Paldean']

    if any(regional in location.text.split() for regional in forms):

        for i in forms:
            t = location.find(string=i)
            if isinstance(t,str):
                regional = t
                break

        dictionary = {'Normal': [], regional: []}

    match form:
        case None:
            if location.find(string='Normal'):
                base_form = []
                regional_form = []

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
                
                base_form = functions.remove_string(base_form)
                regional_form = functions.remove_string(regional_form)

                dictionary['Normal'] = base_form
                dictionary[regional] = regional_form

                return dictionary
            
            else:
                types = []

                for tag in location:
                    a_tag = tag.find('img')
                    if a_tag and not isinstance(a_tag,Tag):
                        continue
                    
                    if pokemon:
                        type_text = functions.elements_atk(a_tag)
                        types.append(type_text)

                    else:
                        try:
                            type_text = a_tag['alt']
                            types.append(type_text)
                        except KeyError:
                            type_text = functions.elements_atk(a_tag)
                            types.append(type_text)

                types = functions.remove_string(types)

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
                    if ty in type_text:
                        types.append(element)
            
            return types

def form_standard_case(main:ResultSet, word:str) -> list:

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

def detect_new_forms(pokemon_name:str, main_table:ResultSet) -> tuple[list,str] | tuple[None,str]:
    #Search for the line that contains <td class="fooevo" colspan="6">
    location = []
    for i,table in enumerate(main_table):
        if table.find('td', {'class': 'fooevo', 'colspan': '6'}):
            location.append(i)

    if location:
        return location,f'{pokemon_name} has Mega'
    else:
        return None,f'{pokemon_name} does not have Mega'
    
def process_multiple_bases(texts:list, bases:list):
    stats = {i: [] for i in texts}
    for n,t in enumerate(stats):
        match n:
            case 0:
                stats[t] = bases[0:6]
            case 1:
                stats[t] = bases[6:12]
            case 2:
                stats[t] = bases[12:18]
            case 3:
                stats[t] = bases[18:24]
    
    return stats