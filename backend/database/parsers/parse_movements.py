# Standard libraries of Python

# Dependencies
from bs4 import NavigableString, Tag, BeautifulSoup

# Libraries
from backend.database.utils import functions

def list_composition(table:BeautifulSoup) -> list[Tag | NavigableString]:
    info = []
    for pos in table.find_all('td'):
        info.append(pos)
    
    content = [item for sublist in info[1:] for item in sublist]
    content = list(filter(lambda x: all(keyword not in str(x[1]) for keyword in ['table', '<br/>']), enumerate(content)))
    scrap = list(map(lambda x: x[1], content))

    return scrap

def obtain_positions(scrap:list):
    
    def obtain_logs():
        logs = []

        for n,i in enumerate(scrap):
            try:
                category = functions.elements_atk(i,1)
                logs.append(n) if category is not None else 0
            except (KeyError,TypeError):
                continue
        
        return logs
    
    def check_list(table:list, index:int, length:int):
        def next_element(index):
            return index + 1
        
        def element_del(table:list, index:int):
            table[index] = 4
            del table[next_key]

        while index < length - 1:
            next_key = next_element(index)

            if (table[index] == 1 and table[next_key] == 3) or (table[index] == 3 and table[next_key] == 1):
                element_del(table,index)
                length = len(table)
                index = next_key
            else:
                index = next_key
        
        return table
    
    locations = obtain_logs()
    range_end = locations[-1] if locations else 0
    ranges = [list(range(i, i+10)) for i in range(1, range_end, 10)]
    counts = list(map(lambda group: sum(1 for num in locations if num in group), ranges))

    group_by = list(filter(lambda count: count > 0, counts))
    length = len(locations)
    check_list(group_by, 0, length)

    return locations, group_by

def execution_pass(to_fix:int):
    if to_fix != 11:
        return [2,3,8,9]
    else:
        return True

def normal_regional(pokemon_ability:dict):
    k = pokemon_ability.keys()
    return True if any([i in ['Alolan','Galarian','Hisuian','Paldean'] for i in k]) else False

def empty_category_fix(to_fix:list, index:int):
    if index == 2:
        to_fix.insert(index, 'Other')
        to_fix.insert(index+1, 'N/A')
        to_fix.insert(index+2, '--')
    else:
        to_fix.insert(index, 'N/A')

def category_fix(to_fix:list, index:int, element:bool):
    if index == 2 and not element:
        to_fix.insert(index,'N/A')
    elif index == 3 and isinstance(to_fix[index], NavigableString):
        to_fix.insert(index,'N/A')
    elif index == 8 or index == 9:
        to_fix.insert(index,'N/A')
    else:
        pass

def eliminate_excess(positions:list[int], scrap:list[Tag|NavigableString]):
    return [element for idx, element in enumerate(scrap) if idx not in positions]

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
                    table[numerator+7], NavigableString
                )
            ) and hasattr(table[numerator+8], 'get') else 9
        ) if len(table) - numerator > 9 else 8

def list_lenght(numerator:int, table:list, limit:str=None, pokemon_ability:dict=None):
    regional = normal_regional(pokemon_ability)
    if not regional:
        last_element = 8
        l = last_element if isinstance(table[numerator+last_element],NavigableString) and table[numerator+last_element] not in ['Gen','Move Tutor','HM'] else 9
    else:
        match limit:
            case 'Z Move' | 'Max Move':
                l = regional_z_max(numerator,table)
            case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
                l = regional_case(numerator,table)

    def internal():
        return l
    
    return internal

def max_z_table_segment(start_index:int, length:int, table:list, indexes:list):
    to_fix = table[start_index:start_index+length]
    for idx in indexes:
        if execution_pass(len(to_fix)) == True:
            break
        
        match idx:
            case 2 | 3:
                if not isinstance(to_fix[idx], NavigableString):
                    element = functions.is_physical_attack(to_fix,idx) if idx == 2 else functions.is_special_attack(to_fix,idx)
                    category_fix(to_fix,idx,element)
                else:
                    empty_category_fix(to_fix,idx)
            case 8 | 9:
                element = functions.is_normal_form(to_fix,idx) if idx == 8 else functions.is_regional_form(to_fix,idx)
                category_fix(to_fix,idx,element)
    
    def internal():
        return to_fix
    
    return internal

def define_table(group, positions, scrap):
    result = []
    index = 0
    for num in group:
        line = positions[index:index + num]
        last_element = line[-1]

        sublist = line + [last_element + 1] if len(line) > 1 else line
        final_positions = sublist[2:] if len(sublist) > 3 else sublist[1:] if len(sublist) == 3 else []
        
        result.extend(final_positions)
        index += num

    main_table = eliminate_excess(result,scrap)

    return main_table

def process_table_recursive(i:int, table:list, limit:str, pokemon_ability:dict=None):
    if i >= len(table):
        return []
    
    l = list_lenght(i, table, limit, pokemon_ability)()
    indexes = execution_pass(l)

    if type(indexes) != bool:
        to_fix = max_z_table_segment(i,l,table,indexes)()
        return [to_fix] + process_table_recursive(i+l,table,limit,pokemon_ability)
    else:
        return [table[i:i+l]] + process_table_recursive(i+l,table,limit,pokemon_ability)