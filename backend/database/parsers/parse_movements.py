# Standard libraries of Python
import functools
from typing import Literal, List

# Dependencies
from bs4 import NavigableString, Tag, BeautifulSoup, ResultSet

# Libraries
from backend.database.utils import functions
from backend.database.utils.functions import remove_string_line

def list_composition(table:BeautifulSoup=None, category:str=None) -> list[Tag | NavigableString]:
    """
    Function to obtain the clean components of the html table where the info is located,
    in order to sort, adjust and fix the data.

    Parameters:
    - table: It must be a BeautifulSoup object representing the HTML table.
    - category: A string that specify the category of the data (optional).

    Returns:
    - A list of BeatifulSoup Tag or NavigableString objects after filtering and processing
    
    Functions:
    - egg_move_last_line(): Determines the last relevant line in the table based on the presence of an 'img' tag.
        Parameters:
        - scrap: The BeautifulSoup object representing the table.
        Returns:
        - An integer representing the index of the last relevant line in the table.
    """

    def egg_move_last_line(scrap:List[Tag]=None):
        """
        Determine the last relevant line in the table based on the presence of an 'img' tag.

        Returns:
        - An integer representing the index of the last relevant line in the table.
        """
        lines = [list(range(i,i+8)) for i in range(0,len(scrap),9)]

        for line in lines:
            element = line[-1]
            content = scrap[element]
            if content.find('img') is None:
                break
        
        return element - 7
    
    info = [pos for pos in table.find_all('td')]
    init_of_data = info[1:]
    scrap = [item for sublist in init_of_data for item in sublist]
    
    if category == 'Egg Move':
        last_line = egg_move_last_line(scrap)
        content_before = scrap[:last_line]
        content_after = scrap[last_line:]
        filtered_content_after = list(filter(
            lambda x: all(keyword not in str(x[1]) for keyword in ['table', '<br/>']),
            enumerate(content_after, start=last_line)
        ))
        scrap = content_before + [item[1] for item in filtered_content_after]
    
    else:
        content = list(filter(
            lambda x: all(keyword not in str(x[1]) for keyword in ['table', '<br/>']),
            enumerate(scrap)
        ))
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

def define_table(group, positions, scrap:list[Tag]):
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
            
def normal_regional(pokemon_ability:dict | list):
    if isinstance(pokemon_ability,dict):
        k = pokemon_ability.keys()
        return True if any([i in ['Alolan','Galarian','Hisuian','Paldean'] for i in k]) else False
    elif isinstance(pokemon_ability,list):
        return False

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

def egg_move_fix(start_index:int, length:int, table:List[Tag]) -> list[Tag | NavigableString]:
    """
    Fixes specific issues in the egg move section of the table.

    Parameters:
    - start_index: The starting index in the table from where the section begins.
    - length: The length of the section to be fixed.
    - table: A list of BeautifulSoup Tag objects representing the table rows.

    Returns:
    - A list of Tag objects after applying the fixes.
    """
    
    def regional_img_process(to_fix:List[Tag]):
        """
        Process and fix regional images in the section.
        
        Parameters:
        - to_fix: The list of Tag objects to be fixed.
        """
        
        # Fix the error in Serebii.net html, when it closes the tag of corresponding to regional form img with <img\> in the first element
        html = to_fix[data_location]
        soup = BeautifulSoup(str(html), 'html.parser')

        img_tag = soup.find_all('img')
        if img_tag:
            values = [img.get('alt') for img in img_tag]
            to_fix[7] = values[0] # Change the original img table with the normal form Pokémon
            to_fix.insert(8, values[1]) # Add the regional form Pokémon
    
    @remove_string_line('Details')
    def general_process(to_fix:List[Tag], string:str):
        """
        General processing to remove 'Details' entry if present.
        
        Parameters:
        - to_fix: The list of Tag objects to be fixed.
        - string: A string parameter (additional functionality can be added here).
        """

        print(f'Processing string: {string}')

    to_fix = table[start_index:start_index + length]

    # The seventh and eighth element is always the table with regional forms, or with the 'Details' URL with possible parents to inherith egg move
    data_location = 7 if length == 8 else 8

    # Process the table where the normal and regional form are located in the html Serebii.net
    regional_img_process(to_fix)
    general_process(to_fix,'Details')

def max_z_table_segment(start_index:int, length:int, table:list, indexes:list):
    to_fix = table[start_index:start_index+length]
    for idx in indexes:
        if execution_pass(len(to_fix),'Max Move') == True:
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

def execution_pass(to_fix:int, category:Literal['Max Move', 'Z Move']):
    match category:
        case 'Max Move':
            if to_fix != 11:
                return [2,3,8,9]
            else:
                return True

def list_lenght(numerator:int, table:list[Tag], limit:str=None, regional_form:bool=None):
    if not regional_form:
        last_element = 9
        l = last_element if limit != 'Max Move' else 11
    
    else:
        match limit:
            case 'Egg Move':
                data_location = 1
                l = 8 if table[data_location].text != 'BDSP Only' else 9
            case 'Z Move' | 'Max Move':
                l = regional_z_max(numerator,table)
            case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
                l = regional_case(numerator,table)

    def internal():
        return l
    
    return internal

def process_table_recursive(i:int, table:list, limit:str, regional_form:bool=None, category:Literal['Max Move','Egg Move']=None):
    if i >= len(table):
        return []
    
    l = list_lenght(i, table, limit, regional_form)()

    match category:
        case 'Max Move':
            indexes = execution_pass(l,category)
            if type(indexes) != bool:
                to_fix = max_z_table_segment(i,l,table,indexes)()
                return [to_fix] + process_table_recursive(i+l,table,limit,regional_form,category)
            else:
                return [table[i:i+l]] + process_table_recursive(i+l,table,limit,regional_form,category)
        
        case 'Egg Move':
            line = egg_move_fix(i,l,table)
            l += 1
            return [line] + process_table_recursive(i+l,table,limit,regional_form,category)