# Standard libraries of Python

# Dependencies
from bs4 import NavigableString, Tag

# Libraries
from backend.database.utils.functions import elements_atk

def normal_regional(pokemon_ability:dict):
    k = pokemon_ability.keys()
    return True if any([i in ['Alolan','Galarian','Hisuian','Paldean'] for i in k]) else False

def regional_case(numerator:int, table:list[Tag]):
    last_element = 11
    if hasattr(table[numerator+9],'get'):
        return last_element if numerator == 0 or isinstance(table[numerator+9].get('alt',''),str) else 10
    else:
        return last_element - 1

def regional_z_max(numerator:int, table:list[Tag]):
    last_element = 11
    if hasattr(table[numerator+3],'get'):
        return last_element if numerator == 0 or isinstance(table[numerator+8].get('alt',''),str) else 10
    else:
        return (10 if any(
                word in table[numerator+7].get('alt','')
                for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean', 'Normal'] if not isinstance(
                    table[numerator+7], NavigableString))
            and hasattr(table[numerator+8], 'get') else 9
        ) if len(table) - numerator > 9 else 8

def list_lenght(numerator:int, table:list, limit:str=None):
    regional = normal_regional()
    if not regional:
        last_element = 8
        l = last_element if isinstance(table[numerator+last_element],NavigableString) and table[numerator+last_element] not in ['Gen','Move Tutor','HM'] else 9
    else:
        match limit:
            case 'Z Move' | 'Max Move':
                l = regional_z_max(numerator,table)
            case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
                l = regional_case(numerator,table)

    def interna():
        return l
    
    return interna

def execution_pass(to_fix:int):
    if to_fix != 11:
        return [2,3,8,9]
    else:
        return True

def is_physical_attack(table:list[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Physical', 'Other'])

def is_special_attack(table:list[Tag], index:int):
    return any(word in elements_atk(table[index], 1) for word in ['Special'])

def is_normal_form(table:list[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Normal'])

def is_regional_form(table:list[Tag], index:int):
    return any(word in table[index].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean'])

def category_fix(to_fix:list, index:int, element:bool):
    if index == 2 and not element:
        to_fix.insert(index,'N/A')
    elif index == 3 and isinstance(to_fix[index], NavigableString):
        to_fix.insert(index,'N/A')
    elif index == 8 or index == 9:
        to_fix.insert(index,'N/A')
    else:
        pass

def empty_category_fix(to_fix:list, index:int):
    if index == 2:
        to_fix.insert(index, 'Other')
        to_fix.insert(index+1, 'N/A')
        to_fix.insert(index+2, '--')
    else:
        to_fix.insert(index, 'N/A')

def max_z_table_segment(start_index:int, length:int, table:list, indexes:list):
    to_fix = table[start_index:start_index+length]
    for idx in indexes:
        if execution_pass(len(to_fix)) == True:
            break
        
        match idx:
            case 2 | 3:
                if not isinstance(to_fix[idx], NavigableString):
                    element = is_physical_attack(to_fix,idx) if idx == 2 else is_special_attack(to_fix,idx)
                    category_fix(to_fix,idx,element)
                else:
                    empty_category_fix(to_fix,idx)
            case 8 | 9:
                element = is_normal_form(to_fix,idx) if idx == 8 else is_regional_form(to_fix,idx)
                category_fix(to_fix,idx,element)
    
    def internal():
        return to_fix
    
    return internal
                            
def process_table_recursive(i:int, table:list, limit:str):
    if i >= len(table):
        return []
    
    l = list_lenght(i, table, limit)()
    indexes = execution_pass(l)

    if type(indexes) == list:
        to_fix = max_z_table_segment(i,l,table,indexes)
        return [to_fix] + process_table_recursive(i+l,table,limit)
    else:
        return [table[i:i+l]] + process_table_recursive(i+l,table,limit)