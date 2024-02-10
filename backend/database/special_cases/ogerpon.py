"""class for ogerpon special case"""

# Standard Libraries of Python
from itertools import cycle

# Dependencies
from bs4 import Tag

def ogerpon_types(location:Tag):
    from backend.database.src.creature import Pokemon

    text = location.text.replace('\n', '').split()
    masks = [f'{text[i]} {text[i+1]}' for i in range(0,len(text),2)]

    ogerpon_types = Pokemon._get_elemental_types(Pokemon,masks,location)

    return ogerpon_types

def ogerpon_weakness(location:Tag, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    ogerpon_t_m = values[0:18]
    ogerpon_h_m = values[18:36]
    ogerpon_w_m = values[36:54]
    ogerpon_c_m = values[54:72]

    ogerpon_t_m_w = Pokemon._get_list_of_weakness(Pokemon,'ogerpon',None,elemental_types,ogerpon_t_m)
    ogerpon_h_m_w = Pokemon._get_list_of_weakness(Pokemon,'ogerpon',None,elemental_types,ogerpon_h_m)
    ogerpon_w_m_w = Pokemon._get_list_of_weakness(Pokemon,'ogerpon',None,elemental_types,ogerpon_w_m)
    ogerpon_c_m_w = Pokemon._get_list_of_weakness(Pokemon,'ogerpon',None,elemental_types,ogerpon_c_m)

    return ogerpon_t_m_w,ogerpon_h_m_w,ogerpon_w_m_w,ogerpon_c_m_w

def ogerpon_abilities(location:Tag):
    mask_abilities = {}
    terastallised_abilities = {}

    mask_cycle = cycle(range(4))
    terastallised_cicle = cycle(range(4))

    for i in location:
        father = i
        ability = father.text
        if ' Mask ' in ability:
            mask_abilities[ability] = []
            terastallised_abilities[ability] = []
        else:
            continue

    for (i, ability) in enumerate(location):
        try:
            father = ability
            ability = father.text

            if ' Mask ' in ability:
                continue

            ability_text = father.next_element.next.strip()
            to_join = [ability, ability_text]
            result = ''.join(to_join)

            if i < 8:
                # Actualizar diccionario mask_abilities
                master_key_index = next(mask_cycle)
                mask_key = list(mask_abilities.keys())[master_key_index]
                mask_abilities[mask_key] = result
            else:
                # Actualizar diccionario terastallised_abilities
                master_key_index = next(terastallised_cicle)
                terastallised_key = list(terastallised_abilities.keys())[master_key_index]
                terastallised_abilities[terastallised_key] = result

        except TypeError as e:
            print(f'{e}')
            continue