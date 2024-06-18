# Standard libraries of Python
from typing import Literal

# Dependencies
from bs4 import NavigableString, Tag, BeautifulSoup

# Libraries
from backend.database.utils import functions
from backend.database.utils.decorators import solve_img_issue, check_form_category

@check_form_category()
def attack_form_process(boolean:bool=None, key_word:str=None):
    if boolean:
        return key_word
    else:
        return 'N/A'
    
@solve_img_issue()
def pre_evolution_moves(tag:Tag=None, line:list[Tag | NavigableString]=None):
    information = tag.get('alt')
    line[7] = information

    return line

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

    def egg_move_last_line(scrap:list[Tag | NavigableString]=None):
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

def tm_tr_move_fix(start_index:int, length:int, scrap:list[Tag | NavigableString]):
    line = scrap[start_index:start_index + length]

    match length:
        case 11:
            for idx in [2,8,9]:
                result = attack_form_process(line,idx)
                if result:
                    line[idx] = result
            return line
        
        case 10:
            for idx in [2,8,9]:
                result = attack_form_process(line,idx)
                if result != 'N/A':
                    line[idx] = result
                else:
                    line.insert(idx,result)
            
            return line
        
        case _:
            idx = 3
            result = attack_form_process(line,idx)
            line[idx] = result

def egg_move_fix(start_index:int, length:int, scrap:list[Tag | NavigableString], regional:bool=None):
    """
    Fixes specific issues in the egg move section of the table.

    Parameters:
    - start_index: The starting index in the table from where the section begins.
    - length: The length of the section to be fixed.
    - table: A list of BeautifulSoup Tag objects representing the table rows.

    Returns:
    - A list of Tag objects after applying the fixes.
    """
    @solve_img_issue(regional)
    def remove_string(to_fix:list[Tag | NavigableString], string:str=None):
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

    # The seventh and eighth element is always the table with regional forms, or with the 'Details' URL with possible parents to inherith egg move.
    location = 7 if length == 9 or scrap[start_index].text == 'Volt Tackle' else 8

    # Process the table where the normal and regional form are located in the html Serebii.net. Delete the 'Details' string.
    line = remove_string(to_fix,string='Details',data_location=location)

    idx = 2
    make_contact = attack_form_process(line,idx)
    if make_contact != 'N/A':
        line[idx] = make_contact

    return line

def max_z_table_segment(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, indexes:list[int]=None):
    """
    Fixes segments of a table based on specific indexes and categories for 'Max Move' or 'Z Move' entries.

    Parameters:
    - start_index (int): The starting index in the `table` list from where the segment should be fixed.
    - length (int): The number of elements in the segment to be fixed.
    - table (list): The list of HTML tags and strings to be processed.
    - indexes (list): The list of indexes to be checked and potentially fixed within the segment.

    Returns:
    - function: A nested function `internal` that, when called, returns the fixed segment.

    The function operates as follows:
    1. Extracts the segment of the table to be fixed using `start_index` and `length`.
    2. Iterates over the provided `indexes` and performs fixes based on the `idx` value:
        - For indexes 2 and 3, checks if the element is a physical or special attack and fixes the category accordingly.
        - For indexes 8 and 9, checks if the element is a normal or regional form and fixes the category accordingly.
    3. If the `execution_pass` function returns `True`, it breaks out of the loop early.
    4. Returns the fixed segment via a nested function `internal`.

    Example:
        >>> table = [NavigableString('Example')] * 12  # Example table data
        >>> result_func = max_z_table_segment(0, 12, table, [2, 3, 8, 9])
        >>> fixed_segment = result_func()
        >>> print(fixed_segment)
        [NavigableString('Example'), ...]  # Fixed segment data
    """

    line = scrap[start_index:start_index+length]
    for idx in indexes:        
        match idx:
            case 2 | 3:
                make_contact = attack_form_process(line,idx)
                if make_contact == 'N/A':
                    line.insert(idx,make_contact)
                elif make_contact == 'Other' and idx == 2:
                    functions.empty_category_fix(line,idx)
                else:
                    line[idx] = make_contact

            case 8 | 9:
                form = attack_form_process(line,idx)
                if form == 'N/A':
                    line.insert(idx,form)
                elif form and len(line) != 11 and form in ['Alolan_form', 'Galarian_form', 'Hisuian_form', 'Paldean_form']:
                    line.insert(idx, 'N/A')
                else:
                    line[idx] = form
    
    def internal() -> list[Tag | NavigableString]:
        return line
    
    return internal

def move_tutor():
    pass

def list_lenght(numerator:int, scrap:list[Tag | NavigableString]=None,
    category:Literal['TM','TR','HM','Z Move','Max Move',
        'Technical Machine', 'Technical Record', 'Hidden Machine', 'Level Up', 'Pre_evolution']=None,
    regional_form:bool=None) -> Literal[8, 9, 10, 11]:
    
    """
    Function that permits the recursive table process, in order to know the amount of elements 
    that certain line needs to have in order to be correct in the main table.

    Parameters:
    - numerator: The position in the list to start from.
    - scrap: The list of HTML tags and strings to process.
    - category: The category to evaluate.
    - regional_form: Boolean indicating if it is a regional form.

    Returns:
    - The number of elements that the line needs to have in order to be correct in the main table.
    """

    if not regional_form:
        if any(
            word in category
            for word in 
            ['Technical Machine','Technical Record', 'Hidden Machine', 'Level Up',
             'TM','TR','HM', 'BDSP Technical Machine']
        ):
            length = 8
        elif category == 'Pre_evolution':
            length = 10
        elif category == 'Max Move':
            length = 11
        elif category != 'Pre_evolution' and category != 'Max Move':
            length = 9
        
        return length
    
    match category:
        case 'Egg Move':
            data_location = 1
            if 'Only' in scrap[numerator+data_location].text or scrap[numerator].text == 'Volt Tackle':
                length = 10
            else:
                length = 9
        case 'Z Move' | 'Max Move':
            length = functions.regional_z_max(numerator,scrap)
        case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
            length = functions.regional_case(numerator,scrap)
    
    return length

def make_it_table(start_index:int=0, scrap:list[Tag | NavigableString]=None,
    category:Literal['TM','TR','HM','Z Move','Max Move',
        'Technical Machine', 'Technical Record', 'Hidden Machine', 'Level Up', 'Pre_evolution']=None,
    regional_form:bool=None):
    
    """
    Creates a table of elements by recursively processing lines from the input list of HTML tags and strings.

    Parameters:
    - start_index (int): The starting index in the `scrap` list from where the processing should begin. Default is 0.
    - scrap (list[Tag | NavigableString]): A list of HTML tags and navigable strings to be processed.
    - category: The category of elements to process. It determines the specific logic applied to each line.
    - regional_form (bool): A flag indicating whether the elements belong to a regional form.

    Returns:
    - list: A list of processed lines, where each line is either a list of elements from the `scrap` list or a modified segment based on the category-specific logic.

    The function operates as follows:
    1. Checks if the `start_index` is out of bounds for the `scrap` list. If so, returns an empty list.
    2. Determines the number of elements (`items_in_list`) in the current line to be processed using the `list_lenght` function.
    3. Processes the line based on the specified `category`:
        - For 'Max Move': Uses `execution_pass` to get indexes and processes with `max_z_table_segment` or returns the segment directly.
        - For 'Egg Move': Fixes the line using `egg_move_fix`.
        - For 'Pre_evolution': Fixes the line using `pre_evolution_moves`.
    4. Recursively calls itself to process the next segment of the `scrap` list.

    Example:
        >>> from bs4 import BeautifulSoup
        >>> html = "<div>some html content</div>"
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> elements = list(soup.children)
        >>> make_it_table(0, elements, 'Egg Move', False)
        [['some processed content based on egg move logic']]
    """

    length = len(scrap)
    if start_index >= length:
        return []
    
    # int that determines the amount of elements in the the line to be fixed.
    items_in_list = list_lenght(start_index,scrap,category,regional_form)

    match category:
        case 'Max Move':
            # Determine if there is indexes to be processed
            indexes = [2,3,8,9]
            line = max_z_table_segment(start_index,items_in_list,scrap,indexes)()
            return [line] + make_it_table(start_index+items_in_list,scrap,category,regional_form)
        
        case 'Egg Move':
            line = egg_move_fix(start_index,items_in_list,scrap,regional_form)
            return [line] + make_it_table(start_index+items_in_list,scrap,category,regional_form)
        
        case 'Pre_evolution':
            to_fix = scrap[start_index:start_index+items_in_list]
            line = pre_evolution_moves(line=to_fix,data_location=7)
            return [line] + make_it_table(start_index+items_in_list,scrap,category)
        
        case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
            line = tm_tr_move_fix(start_index,items_in_list,scrap)
            return [line] + make_it_table(start_index+items_in_list,scrap,category,regional_form)