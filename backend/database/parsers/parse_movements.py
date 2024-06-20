# Standard libraries of Python
from typing import Literal

# Dependencies
from bs4 import NavigableString, Tag, BeautifulSoup

# Libraries
from backend.database.utils import functions
from backend.database.utils.decorators import solve_img_issue, check_form_category, catt_form_logic

@catt_form_logic()
def obtain_catt_form(answer:bool|str=None, line:list[Tag | NavigableString]=None, idx:int=None, catt_form:str|bool=None):
    """
    Functions decorated to handle form category logic and attack form processing.

    Functions:
    - obtain_catt_form(answer: bool | str = None, line: list[Tag | NavigableString] = None, idx: int = None, catt_form: str | bool = None) -> list[Tag | NavigableString]:
        Processes and updates a line with a categorical form.

    Parameters:
    - answer (bool | str, optional): The result of categorical form logic.
    - line (list[Tag | NavigableString], optional): The list of BeautifulSoup Tag objects and NavigableStrings to modify.
    - idx (int, optional): The index in the line where the categorical form is applied.
    - catt_form (str | bool, optional): The categorical form to apply.

    Returns:
    - list[Tag | NavigableString]: The modified line after applying the categorical form logic.
    """
    if isinstance(answer,bool):
        line[idx] = catt_form
    elif isinstance(answer,str):
        line.insert(idx,answer)

    return line
        
@check_form_category()
def attack_form_process(boolean:bool=None, key_word:str=None):
    """
    Determines the attack form based on boolean logic.

    Parameters:
    - boolean (bool, optional): Boolean flag indicating if the attack form is valid.
    - key_word (str, optional): The key word representing the attack form.

    Returns:
    - str: The determined attack form or 'N/A' if not valid.
    """
    if boolean:
        return key_word
    else:
        return 'N/A'

def list_composition(html:BeautifulSoup=None, category:Literal['Egg Move']=None) -> list[Tag | NavigableString]:
    """
    Extracts and processes clean components from an HTML table represented as a BeautifulSoup object.

    Args:
    - html (BeautifulSoup, optional): The BeautifulSoup object representing the HTML table. If not provided,
      the function will return an empty list.
    - category (Literal['Egg Move'], optional): Specifies the category of the data. If specified as 'Egg Move',
      it processes the table differently to filter out specific content related to egg moves.

    Returns:
    - list[Union[Tag, NavigableString]]: A list of BeautifulSoup Tag objects and NavigableStrings after filtering and processing.
      If no 'html' parameter is provided or no relevant data is found, an empty list is returned.

    Functions:
    - egg_move_last_line(scrap: list[Union[Tag, NavigableString]]) -> int:
        Determines the index of the last relevant line in the table based on the presence of an 'img' tag.

        Args:
        - scrap (list[Union[Tag, NavigableString]]): The list of BeautifulSoup Tag objects and NavigableStrings representing the table.
          It should contain the content extracted from the HTML table.

        Returns:
        - int: The index of the last relevant line in the table. If no relevant line is found or 'scrap' is empty,
          it returns -1.

    Details:
    - This function processes an HTML table represented as a BeautifulSoup object ('html'). It extracts data from table cells ('td')
      and filters out unwanted content like nested tables and line breaks ('<br/>').
    - If 'category' is specified as 'Egg Move', it identifies the end of relevant data by checking for the presence of an 'img' tag
      and processes the table accordingly.
    - The function 'egg_move_last_line' is a helper function used internally to determine where relevant data ends in the table,
      based on specific criteria related to 'Egg Move' category.

    Example Usage:
    >>> html = BeautifulSoup(html_content, 'html.parser')
    >>> result = list_composition(html, category='Egg Move')
    >>> print(result)
    [Tag1, Tag2, NavigableString1, ...]
    """
    def egg_move_last_line(scrap:list[Tag | NavigableString]=None):
        """
        Determines the index of the last relevant line in the table based on the presence of an 'img' tag.

        Args:
        - scrap (list[Union[Tag, NavigableString]]): The list of BeautifulSoup Tag objects and NavigableStrings representing the table.
          It should contain the content extracted from the HTML table.

        Returns:
        - int: The index of the last relevant line in the table. If no relevant line is found or 'scrap' is empty,
          it returns -1.

        Details:
        - This function iterates through the 'scrap' list to find the last line that contains relevant data, identified
          by the presence of an 'img' tag. It helps determine the endpoint of content extraction for specific categories
          like 'Egg Move'.
        - The function assumes 'scrap' contains content from an HTML table, where relevant lines are separated by a fixed
          number of elements (typically 9 elements per line).

        Example Usage:
        >>> scrap = [Tag1, NavigableString1, Tag2, ...]
        >>> last_line_index = egg_move_last_line(scrap)
        >>> print(last_line_index)
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
    """
    Obtains positions of specific elements based on conditions within the scrap list.

    Parameters:
    - scrap (list[Tag | NavigableString], optional): A list of BeautifulSoup Tag objects and NavigableStrings.

    Returns:
    - list[int]: A refined list of positions after processing based on specific conditions.

    Functions:
    - obtain_logs(): Inner function that collects indices of elements satisfying certain conditions.
    - check_list(positions:list[int]=None, index:int=None, length:int=None): Inner function that refines positions based on sequential conditions.

    Example:
        >>> scrap = [Tag(), NavigableString('Example'), Tag(), Tag(), NavigableString('Another'), Tag()]
        >>> positions = obtain_positions(scrap)
        >>> print(positions)
        [1, 3, 4]

    Notes:
    - This function operates on a scrap list assumed to contain relevant elements.
    - The `functions.elements_atk` function is referenced in `obtain_logs` for element categorization.
    """
    def obtain_logs():
        """
        Collects indices of elements in the scrap list that satisfy specific conditions.

        Returns:
        - list[int]: A list of indices where elements meet the condition.

        Notes:
        - Uses `functions.elements_atk` to categorize elements.
        """
        logs = []

        for n,i in enumerate(scrap):
            try:
                category = functions.elements_atk(i,1)
                logs.append(n) if category is not None else 0
            except (KeyError,TypeError):
                continue
        
        return logs
    
    def check_list(positions:list=None, index:int=None, length:int=None):
        """
        Refines positions based on sequential conditions.

        Parameters:
        - positions (list[int], optional): The list of positions to be refined.
        - index (int, optional): The starting index for checking positions.
        - length (int, optional): The length of the positions list.

        Returns:
        - list[int]: The refined list of positions after processing.

        Notes:
        - Modifies the positions list in place.
        """
        def next_element(index:int):
            """
            Calculates the index of the next element.

            Parameters:
            - index (int): The current index.

            Returns:
            - int: The index of the next element.
            """
            return index + 1
        
        def element_del(table:list, index:int):
            """
            Deletes an element from the positions list and adjusts length.

            Parameters:
            - table (list[int]): The list of positions.
            - index (int): The index of the element to delete.
            """
            table[index] = 4
            del table[next_key]

        while index < length - 1:
            next_key = next_element(index)

            # Search in the list if the next key is three (3) or one (1), depending on the initial value in position[index]
            if (positions[index] == 1 and positions[next_key] == 3) or (positions[index] == 3 and positions[next_key] == 1):
                element_del(positions,index)
                length = len(positions)
                index = next_key
            else:
                index = next_key
        
        return positions
    
    # From the scrap, obtain the registry of the location of duplicated data
    locations = obtain_logs()
    range_end = locations[-1] if locations else 0

    # Construct the ranges from 1 to 10 and the ones that follows, in order to count the amount of numbers that appears in them
    ranges = [list(range(i,i+10)) for i in range(1,range_end,10)]

    # If the position has [2,3,4,5,...], then the sum that start from range 10 to 10, will be 4
    counts = list(map(lambda group: sum(1 for num in locations if num in group), ranges))

    # Eliminate the zero (0) numbers in the list
    group_by = list(filter(lambda count: count > 0, counts))
    length = len(locations)
    check_list(group_by, 0, length)

    return locations, group_by

def define_table(group:list[int]=None, positions:list[int]=None, scrap:list[Tag]=None):
    """
    Defines positions in a table based on groups and specific positions within a scrap list.

    Parameters:
    - group (list of int, optional): List defining the number of positions in each group.
    - positions (list of int, optional): List of specific positions within the scrap list.
    - scrap (list of Tag, optional): List of BeautifulSoup Tag objects to process.

    Returns:
    - list of Tags and NavigableString: A main table after eliminating excess positions.

    Algorithm:
    - Initializes an empty result list.
    - Iterates over each number in the group list:
      - Constructs a line of positions from the positions list based on the current index and number.
      - Determines the last element in the line.
      - Creates a sublist that includes the last element plus one if the line has more than one element.
      - Extends the result list with the final positions from the sublist.
    - Processes the main table by eliminating excess positions using a function `functions.eliminate_excess`.

    Example:
        >>> group = [3, 2]
        >>> positions = [1, 2, 3, 4, 5]
        >>> scrap = [Tag(), Tag(), Tag(), Tag(), Tag()]
        >>> main_table = define_table(group, positions, scrap)
        >>> print(main_table)
        [3, 4, 5]

    Notes:
    - The function assumes positions are 1-based indexing.
    - The `functions.eliminate_excess` function is used to refine the main table positions.
    """
    result = []
    index = 0
    for num in group:
        line = positions[index:index + num]
        last_element = line[-1]

        # Create a new sublist that contains the next value of the last_element
        sublist = line + [last_element + 1] if len(line) > 1 else line

        # Take a definitive positions for the main_table, the last three (3) or two (2) elements, depending on the lenght of the list
        final_positions = sublist[2:] if len(sublist) > 3 else sublist[1:] if len(sublist) == 3 else []
        
        # Save the data inside the empty list.
        result.extend(final_positions)

        # Increment the index by the amount of elements that were processed
        index += num

    main_table = functions.eliminate_excess(result,scrap)

    return main_table

def tm_tr_move_fix(start_index:int, length:int, scrap:list[Tag | NavigableString],
        category:Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move','Technical Machine', 'Technical Record',
        'Hidden Machine', 'Level Up', 'Pre_evolution', 'Egg Move']=None):
    """
    Fixes specific issues in the TM/TR/HM move sections of the table based on the provided category.

    Parameters:
    - start_index (int): The starting index in the `scrap` list from where the section begins.
    - length (int): The length of the section to be fixed.
    - scrap (list[Tag | NavigableString]): A list of BeautifulSoup Tag objects representing the table rows.
    - category (Literal): The category to evaluate, affecting the logic applied to each index.

    Returns:
    - list[Tag | NavigableString]: A list of Tag objects after applying the fixes.

    The function operates as follows:
    1. Extracts the segment to be fixed using `start_index` and `length`.
    2. Based on the length of the segment, it processes the relevant indexes:
        - For segments of length 10 or 11, it iterates over indexes 3, 8, and 9, and fixes each using `attack_form_process` and `obtain_catt_form`.
        - For other lengths, it processes index 3 only.
    3. Returns the fixed segment.

    Example:
        >>> from bs4 import BeautifulSoup, NavigableString
        >>> html = "<div>...</div>"  # Example HTML content
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> elements = list(soup.children)
        >>> fixed_section = tm_tr_move_fix(0, 10, elements, 'TM')
        >>> print(fixed_section)
        [<Tag ...>, ...]  # Fixed segment data
    """
    line = scrap[start_index:start_index + length]

    match length:
        case 10 | 11:
            iterator = [3,8,9]
            for idx in iterator:
                answer = attack_form_process(line,idx,category)
                line = obtain_catt_form(line=line,index=idx,category=category,catt_form=answer)
                
            return line
            
        case _:
            idx = 3
            answer = attack_form_process(line,idx,category)
            line = obtain_catt_form(line=line,index=idx,category=category,catt_form=answer)

            return line

def egg_move_fix(start_index:int, length:int, scrap:list[Tag | NavigableString],
        category:Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move','Technical Machine', 'Technical Record',
        'Hidden Machine', 'Level Up', 'Pre_evolution', 'Egg Move']=None, regional:bool=None):
    """
    Fixes specific issues in the egg move section of the table.

    Parameters:
    - start_index (int): The starting index in the `scrap` list from where the section begins.
    - length (int): The length of the section to be fixed.
    - scrap (list[Tag | NavigableString]): A list of BeautifulSoup Tag objects representing the table rows.
    - regional (bool, optional): Indicates if the elements belong to a regional form.

    Returns:
    - list[Tag | NavigableString]: A list of Tag objects after applying the fixes.

    The function operates as follows:
    1. Defines an inner function `remove_string` to process and fix regional images in the section.
    2. Extracts the segment to be fixed using `start_index` and `length`.
    3. Determines the location of the table with regional forms or the 'Details' URL.
    4. Uses `remove_string` to delete the 'Details' string from the segment.
    5. Processes the segment to fix the category based on the attack form and returns the fixed segment.

    Example:
        >>> from bs4 import BeautifulSoup, NavigableString
        >>> html = "<div>...</div>"  # Example HTML content
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> elements = list(soup.children)
        >>> fixed_section = egg_move_fix(0, 9, elements, False)
        >>> print(fixed_section)
        [<Tag ...>, ...]  # Fixed segment data
    """
    @solve_img_issue(regional)
    def remove_string(to_fix:list[Tag | NavigableString], string:str=None):
        """
        Process and fix regional images in the section.

        Parameters:
        - to_fix (list[Tag | NavigableString]): The list of Tag objects and NavigableString to be fixed.
        - string (str, optional): Text to be deleted.

        Returns:
        - list[Tag | NavigableString]: The fixed list of Tag objects and NavigableString.
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

    idx = 2 if length == 9 or scrap[start_index].text == 'Volt Tackle' else 3
    answer = attack_form_process(line,idx,category)
    line = obtain_catt_form(line=line,index=idx,category=category,catt_form=answer)

    return line

def max_z_table_segment(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, indexes:list[int]=None,
                        category:Literal[
                        'TM','TR','HM','Z Move','Max Move',
                        'Technical Machine', 'Technical Record', 'Hidden Machine',
                        'Level Up', 'Pre_evolution', 'Egg Move']=None,):
    """
    Fixes segments of a table based on specific indexes and categories for 'Max Move' or 'Z Move' entries.

    Parameters:
    - start_index (int): The starting index in the `scrap` list from where the segment should be fixed.
    - length (int): The number of elements in the segment to be fixed.
    - scrap (list[Tag | NavigableString]): The list of HTML tags and strings to be processed.
    - indexes (list[int]): The list of indexes to be checked and potentially fixed within the segment.
    - category (Literal): The category to evaluate, affecting the logic applied to each index.

    Returns:
    - list: The fixed segment of the table based on the provided indexes and category-specific logic.

    The function operates as follows:
    1. Extracts the segment of the table to be fixed using `start_index` and `length`.
    2. Iterates over the provided `indexes` and performs fixes based on the `idx` value:
        - For indexes 2 and 3, checks if the element is a physical or special attack and fixes the category accordingly.
        - For indexes 8 and 9, checks if the element is a normal or regional form and fixes the category accordingly.
    3. If the `answer` is 'N/A' and the line length is not 9, 10, or 11, it calls `empty_category_fix` and removes the index from the list.
    4. Otherwise, it calls `obtain_catt_form` to fix the category based on the answer.

    Example:
        >>> from bs4 import NavigableString
        >>> scrap = [NavigableString('Example')] * 12  # Example table data
        >>> result = max_z_table_segment(0, 12, scrap, [2, 3, 8, 9], 'Max Move')
        >>> print(result)
        [NavigableString('Example'), ...]  # Fixed segment data
    """
    line = scrap[start_index:start_index+length]
    line_length = len(line)
    for idx in indexes:
        answer = attack_form_process(line,idx,category)
        if answer == 'N/A' and line_length not in [9,10,11]:
            functions.empty_category_fix(line,idx)
            indexes.remove(idx)
        else:
            line = obtain_catt_form(line=line,index=idx,category=category,catt_form=answer)
    
    return line

@solve_img_issue()
def pre_evolution_moves(tag:Tag=None, line:list[Tag | NavigableString]=None):
    information = tag.get('alt')
    line[7] = information

    return line

def move_tutor():
    pass

def list_lenght(numerator:int, scrap:list[Tag | NavigableString]=None,
    category:Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine', 'Technical Record',
                     'Hidden Machine', 'Level Up', 'Pre_evolution', 'Egg Move']=None,
    regional_form:bool=None) -> Literal[8, 9, 10, 11]:
    
    """
    Determines the number of elements that a line in the main table needs to have to be correct, 
    based on the given category and regional form.

    Parameters:
    - numerator (int): The starting position in the `scrap` list.
    - scrap (list[Tag | NavigableString]): The list of HTML tags and strings to process.
    - category (Literal): The category to evaluate, affecting the number of elements required.
    - regional_form (bool): Indicates if the elements belong to a regional form.

    Returns:
    - int: The number of elements that the line needs to have to be correct in the main table.
           Possible values are 8, 9, 10, or 11.
    """

    if not regional_form:
        if any(
            word in category
            for word in 
            ['Technical Machine', 'Technical Record', 'Hidden Machine', 'Level Up',
             'TM', 'TR', 'HM', 'BDSP Technical Machine']
        ):
            length = 8
        elif category == 'Pre_evolution':
            length = 10
        elif category == 'Max Move':
            length = 11
        else:
            length = 9
        
        return length
    
    match category:
        case 'Egg Move':
            data_location = 1
            if 'Only' in scrap[numerator + data_location].text or scrap[numerator].text == 'Volt Tackle':
                length = 10
            else:
                length = 9
        case 'Z Move' | 'Max Move':
            length = functions.regional_z_max(numerator, scrap)
        case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
            length = functions.regional_case(numerator, scrap)
    
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
        - For 'Max Move': Uses `max_z_table_segment` to process specific indexes or returns the segment directly.
        - For 'Egg Move': Fixes the line using `egg_move_fix`.
        - For 'Pre_evolution': Fixes the line using `pre_evolution_moves`.
        - For 'TM', 'Technical Machine', 'TR', 'Technical Record', 'HM', 'Hidden Machine': Fixes the line using `tm_tr_move_fix`.
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

    # Determine the amount of elements in the line to be processed.
    items_in_list = list_lenght(start_index,scrap,category,regional_form)

    match category:
        case 'Max Move':
            # Determine if there are indexes to be processed
            indexes = [2,3,8,9]
            line = max_z_table_segment(start_index,items_in_list,scrap,indexes,category)
            return [line] + make_it_table(start_index + items_in_list,scrap,category,regional_form)
        
        case 'Egg Move':
            line = egg_move_fix(start_index,items_in_list,scrap,regional_form)
            print(start_index)
            return [line] + make_it_table(start_index + items_in_list,scrap,category,regional_form)
        
        case 'Pre_evolution':
            to_fix = scrap[start_index:start_index + items_in_list]
            line = pre_evolution_moves(line=to_fix,data_location=7)
            return [line] + make_it_table(start_index + items_in_list,scrap,category)
        
        case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
            line = tm_tr_move_fix(start_index,items_in_list,scrap,category)
            return [line] + make_it_table(start_index + items_in_list,scrap,category,regional_form)