# Special Functions in order for main class more legible

from bs4 import Tag,ResultSet

def elemental_types(location:Tag) -> list:
    types = []
    for tag in location:
        a_tag = tag.find('img')
        if a_tag:
            type_text = a_tag['alt']
            types.append(type_text)

    s = 'Attacking Move Type: ','-type'
    for string in s:
        types = list(map(lambda x: x.replace(string,''),types))
    
    return types

def get_parents(parents: list) -> dict:
    pokemon_groups = {}
    current_group = parents[0]
    pokemon_groups[current_group] = []

    for parent in parents[1:]:
        pokemon_groups[current_group].append(parent)
    
    return pokemon_groups

def process_hidden_ability(tag:Tag, abilities_dict:dict, form_abilities_dict:dict, skip_next_flag:bool, form_abilities_flag:bool):
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
    if "Form" in father:
        form_abilities_flag = True
    return form_abilities_flag

def find_table_by_class(gen:int, main_table:ResultSet, class_name: str, index: int) -> ResultSet:
    if gen != 8:
        return main_table[index].find_all('td', {'class': class_name})
    else:
        return main_table[index + 1].find_all('td', {'class': class_name})

def stats_calculation(stat:str, base:int, EV:int, level:int=50, nature=1, IV=31):
    if stat == 'hp':
        hp = ((IV+2*base+(EV/4))*level/100)+10+level
        return hp
    else:
        st =  (((IV + 2 * base + (EV/4) ) * level/100 ) + 5) * nature
        return st

def detect_new_forms(main_table:ResultSet):
    # Buscar todas las tablas en el primer div
    tables = main_table[0].find_all('table', {'class': 'dextable'})

    # Buscar la posición exacta de la línea con <td class="fooevo" colspan="6">
    for i, table in enumerate(tables):
        if table.find('td', {'class': 'fooevo', 'colspan': '6'}):
            break
    
    return i