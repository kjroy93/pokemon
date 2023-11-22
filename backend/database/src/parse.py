# Special Functions in order for main class more legible

from bs4 import Tag

def get_parents(parents: list) -> dict:
    # Crear un diccionario vacío para almacenar los grupos de Pokémon
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

        # Verificar si se están procesando habilidades de Form
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