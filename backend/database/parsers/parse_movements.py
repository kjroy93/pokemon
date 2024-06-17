# Standard libraries of Python
from typing import Literal, List

# Dependencies
from bs4 import NavigableString, Tag, BeautifulSoup, ResultSet

# Libraries
from backend.database.utils import functions
from backend.database.utils.functions import text_image_deletion

def list_composition(html:BeautifulSoup=None, category:Literal['Egg Move']=None) -> list[Tag | NavigableString]:
    """
    Function to obtain the clean components of the html table where the info is located,
    in order to sort, adjust and fix the data.

    Parameters:
    - html: It must be a BeautifulSoup object representing the HTML table.
    - category: A string that specify the category of the data (optional).

    Returns:
    - A list of BeatifulSoup Tag or NavigableString objects after filtering and processing
    
    Functions:
    - egg_move_last_line(scrap): Determines the last relevant line in the table based on the presence of an 'img' tag.
        Parameters:
        - scrap: The BeautifulSoup object representing the table.
        Returns:
        - An integer representing the index of the last relevant line in the table.
    """

    def egg_move_last_line(scrap:List[Tag | NavigableString]=None):
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
    
    info = [pos for pos in html.find_all('td')]
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

def obtain_positions(scrap:list[Tag | NavigableString]=None):
    
    def obtain_logs():
        logs = []

        for n,i in enumerate(scrap):
            try:
                category = functions.elements_atk(i,1)
                logs.append(n) if category is not None else 0
            except (KeyError,TypeError):
                continue
        
        return logs
    
    def check_list(positions:list=None, index:int=None, length:int=None):
        def next_element(index:int):
            return index + 1
        
        def element_del(table:list, index:int):
            table[index] = 4
            del table[next_key]

        while index < length - 1:
            next_key = next_element(index)

            if (positions[index] == 1 and positions[next_key] == 3) or (positions[index] == 3 and positions[next_key] == 1):
                element_del(positions,index)
                length = len(positions)
                index = next_key
            else:
                index = next_key
        
        return positions
    
    locations = obtain_logs()
    range_end = locations[-1] if locations else 0
    ranges = [list(range(i,i+10)) for i in range(1,range_end,10)]
    counts = list(map(lambda group: sum(1 for num in locations if num in group), ranges))

    group_by = list(filter(lambda count: count > 0, counts))
    length = len(locations)
    check_list(group_by, 0, length)

    return locations, group_by

def define_table(group:list[int]=None, positions:list[int]=None, scrap:list[Tag]=None):
    result = []
    index = 0
    for num in group:
        line = positions[index:index + num]
        last_element = line[-1]

        sublist = line + [last_element + 1] if len(line) > 1 else line
        final_positions = sublist[2:] if len(sublist) > 3 else sublist[1:] if len(sublist) == 3 else []
        
        result.extend(final_positions)
        index += num

    main_table = functions.eliminate_excess(result,scrap)

    return main_table

def egg_move_fix(start_index:int, length:int, scrap:List[Tag | NavigableString]):
    """
    Fixes specific issues in the egg move section of the table.

    Parameters:
    - start_index: The starting index in the table from where the section begins.
    - length: The length of the section to be fixed.
    - table: A list of BeautifulSoup Tag objects representing the table rows.

    Returns:
    - A list of Tag objects after applying the fixes.
    """
    @text_image_deletion()
    def remove_string(to_fix:List[Tag | NavigableString], string:str=None):
        """
        Process and fix regional images in the section.
        
        Parameters:
        - to_fix: The list of Tag objects and NavigableString to be fixed.
        - string: Text to be deleted.
        """

        try:
            if to_fix[location].text == string:
                del to_fix[location]
        except AttributeError:
            pass
        
        return to_fix

    to_fix = scrap[start_index:start_index + length]

    # The seventh and eighth element is always the table with regional forms, or with the 'Details' URL with possible parents to inherith egg move
    location = 7 if length == 9 or scrap[start_index].text == 'Volt Tackle' else 8

    # Process the table where the normal and regional form are located in the html Serebii.net. Delete the 'Details' string
    fixed = remove_string(to_fix,string='Details',data_location=location)

    return fixed

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

def execution_pass(to_fix:int, category:Literal['Max Move', 'Z Move']=None):
    match category:
        case 'Max Move' | 'Z Move':
            if to_fix != 11:
                return [2,3,8,9]
            else:
                return True

def list_lenght(numerator:int, scrap:list[Tag | NavigableString], category:str=None, regional_form:bool=None):
    if not regional_form:
        last_element = 9 if category != 'Pre_evolution' else 10
        l = last_element if category != 'Max Move' else 11
    
    else:
        match category:
            case 'Egg Move':
                data_location = 1
                l = 10 if (scrap[numerator+data_location].text in ['Only',' Only']) or scrap[numerator].text == 'Volt Tackle' else 9
            case 'Z Move' | 'Max Move':
                l = functions.regional_z_max(numerator,scrap)
            case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
                l = functions.regional_case(numerator,scrap)

    def internal() -> Literal[8, 9, 10, 11]:
        return l
    
    return internal

def process_table_recursive(start_index:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Max Move','Egg Move']=None, regional_form:bool=None):
    length = len(scrap)
    if start_index >= length:
        return []
    
    # int that determines the amount of elements in the the line to be fixed.
    items_in_list = list_lenght(start_index,scrap,category,regional_form)()

    match category:
        case 'Max Move':
            indexes = execution_pass(items_in_list,category)
            if type(indexes) != bool:
                line = max_z_table_segment(start_index,items_in_list,scrap,indexes)()
                return [line] + process_table_recursive(start_index+items_in_list,scrap,category,regional_form)
            else:
                return [scrap[start_index:start_index+items_in_list]] + process_table_recursive(start_index+items_in_list,scrap,category,regional_form)
        
        case 'Egg Move':
            line = egg_move_fix(start_index,items_in_list,scrap)
            return [line] + process_table_recursive(start_index+items_in_list,scrap,category,regional_form)
        
        case 'Pre_evolution':
            line = scrap[start_index:start_index+items_in_list]
            return [line] + process_table_recursive(start_index+items_in_list,scrap,category)