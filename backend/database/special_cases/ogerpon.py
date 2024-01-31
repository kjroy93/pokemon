"""class for ogerpon special case"""

# Dependencies
from bs4 import Tag

def ogerpon_types(location:Tag):
    from backend.database.src.src import Pokemon

    text = location.text.replace('\n', '').split()
    masks = [f'{text[i]} {text[i+1]}' for i in range(0,len(text),2)]

    ogerpon_types = Pokemon._get_elemental_types(Pokemon,masks,location)

    return ogerpon_types

def ogerpon_weakness(location:Tag, elemental_types:list):
    from backend.database.src.src import Pokemon

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