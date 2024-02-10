# Special Functions in order for main class to be more readable
import re
from typing import Literal
from bs4 import Tag,ResultSet

import pandas as pd
from pandas import DataFrame

def number_generator(init:int):
    for number in range(init,1000):
        yield number

def find_table_by_class(gen:int, main_table:ResultSet, class_name:str=None, normal_form:str=None) -> ResultSet:
    """
    Function that goes to the exact class that contains the information, with the information that recives from self.__basic_tables() method in Pokémon class:

    Requirements:

    - gen: Generation.
    - main_table: This is BeautifulSoup HTML.text parser that contains all the information.
    - class_name: The class that needs to be located in the HTML. If there is a None in the Mega evolution class,
    is because the class_name does not matter in that case. Check the private method in Mega_Pokemon.
    - normal_form: WARNING! This only applies if the Pokémon contains a Mega Evolution. This value comes preloaded from the Mega Pokemon class.
    The flag cames with None from default, so it does not need change.
    - index: Proper location of the table. Do not give any value, unless you know what you are doing, in the main center distribution of the webpage.
    
    """
    match normal_form:
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
                return main_table[0].find_all('table', {'class': 'dextable'})
            elif gen >= 8:
                return main_table[1].find_all('table', {'class': 'dextable'})

def find_word(tag):
    text = tag.name == 'td' and 'Form' in tag.text
    text_1 = tag.name == 'td' and 'Standard' in tag.text

    if text:
        return text
    else:
        return text_1

def find_atribute(location):
    return location.br.next_sibling.text.split('\r\n\t\t\t').pop(1)

def remove_string(data:list):
    s = 'Attacking Move Type: ','-type'
    for string in s:
        data = list(map(lambda x: x.replace(string,''),data))

    return data

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
    
def make_dict(elemental:list, v:list):
    return dict(zip(elemental,v))

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

def elements_atk(a_tag:Tag, control:int=None):
    elemental_types = [
    'Normal',
    'Fire',
    'Water',
    'Electric',
    'Grass',
    'Ice',
    'Fight',
    'Poison',
    'Ground',
    'Flying',
    'Psychic',
    'Bug',
    'Rock',
    'Ghost',
    'Dragon',
    'Dark',
    'Steel',
    'Fairy'
    ]

    category = [
        'physical',
        'special',
        'other'
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

def columns_data_type(quantity_of_columns,reshape,egg_moves,moves):
    if quantity_of_columns == 9:
        for i in reshape:
            if moves == None:
                i[0] = i[0].text
            
            i[1] = i[1].text
            i[2] = elements_atk(i[2])
            i[3] = elements_atk(i[3],1)

    elif quantity_of_columns == 8:
        for i in reshape:
            if egg_moves == 'yes':
                del i[7]

            i[0] = i[0].text
            i[1] = elements_atk(i[1])
            i[2] = elements_atk(i[2],1)

def pd_structure(lst:list=None, action:int=None, df:DataFrame=None, moves:Literal['lv']=None, quantity_of_columns:int=9, egg_moves:Literal['no']='yes'):
    """
    Method to convert move set to a DataFrame, that also treats the data type and the shape of the corresponding list.\n

    Parameters:

    - lst: it is a list of lists, that contains the Tag elements from the bs4 scrap from the webpage.
    It can contain any number of dimensions, as the method converts it into the appropriate one.\n

    - action: special character that must be a integer. This controls the route of the function:
        - If it is default (None), it is going to return a DataFrame.\n
        - If it is 1, is going to transfrom the data in the DataFrame to the corresponding type (str or int).\n
        - If it is 2, converts columns of the given DataFrame (modeled by the shape of this same function, so the columns will be the same), to the corresponding type of data. That is, strictly to string type. Just for data coherence.\n

    - df: The corresponding DataFrame to be treated for cases 1 and 2.\n
    - moves: This determines the names of the columns of the DataFrame. The string 'lv' determines the first column as 'lv'. If it is None, the name will be 'tm_hm'.\n
    - quantity_of_columns: self explanatory with the name of the attribute. It must be 9 if you put 'lv'. In any other case, please DO NOT change the value.\n
    - egg_moves: this value determines if the case to eliminate the seventh element in every list, in the list of list (lst), is necessary.
    """
    match action:
        case None:
            info = lst[1:]
            org = [item for sublist in info for item in sublist]
            reshape = [
                org[i:i+quantity_of_columns]
                for i in range(0,len(org),quantity_of_columns)
            ]

            if quantity_of_columns == 9:
                for i in reshape:
                    if moves == None:
                        i[0] = i[0].text
                    
                    i[1] = i[1].text
                    i[2] = elements_atk(i[2])
                    i[3] = elements_atk(i[3],1)

            elif quantity_of_columns == 8:
                for i in reshape:
                    if egg_moves == 'yes':
                        del i[7]

                    i[0] = i[0].text
                    i[1] = elements_atk(i[1])
                    i[2] = elements_atk(i[2],1)
            
            if moves:
                c_names = n_columns(quantity_of_columns,moves)
            else:
                c_names = n_columns(quantity_of_columns)
        
        case 1:
            for i in df:
                df[i] = df[i].apply(lambda x: pd.to_numeric(x,errors='coerce',downcast='integer') if x.isdigit() else str(x))
                df[i] = df[i].replace('—',0)
                df[i] = df[i].replace('--',0)
        
        case 2:
            typing = {
                'atk_name': 'string',
                'type': 'string',
                'category': 'string',
                'description': 'string'
            }

            df = df.astype(typing)
    
    return df if action is not None else pd.DataFrame(reshape,columns=c_names)
        
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
                
                base_form = remove_string(base_form)
                regional_form = remove_string(regional_form)

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
                        type_text = elements_atk(a_tag)
                        types.append(type_text)

                    else:
                        try:
                            type_text = a_tag['alt']
                            types.append(type_text)
                        except KeyError:
                            type_text = elements_atk(a_tag)
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