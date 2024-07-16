# Standard libraries of Python
from typing import Literal, Callable

# Dependencies
from bs4 import NavigableString, Tag

# Libraries
from backend.database.utils import functions
from backend.database.utils.decorators import solve_img_issue, check_form_category, catt_form_logic

@catt_form_logic()
def obtain_catt_form(answer:bool|str=None, line:list[Tag | NavigableString]=None, idx:int=None, catt_form:str|bool=None, *args, **kwargs):
    """
    Functions decorated to handle form category logic and attack form processing.

    Parameters:
    - answer (bool | str, optional): The result of categorical form logic.
    - line (list[Tag | NavigableString], optional): The list of BeautifulSoup Tag objects and NavigableStrings to modify.
    - idx (int, optional): The index in the line where the categorical form is applied.
    - catt_form (str | bool, optional): The categorical form to apply.

    Returns:
    - list[Tag | NavigableString]: The modified line after applying the categorical form logic.
    """
    if isinstance(answer,bool):
        if catt_form not in ['Normal_form', 'Alola_form', 'Alolan_form', 'Galarian_form', 'Hisuian_form', 'Paldean_form'] and idx not in [2,3] and 'Learn' not in catt_form:
            line[idx] = 'normal_form'

            return line
        
        line[idx] = catt_form.lower()
    
    elif isinstance(answer,str) or not answer:
        line.insert(idx,'N/A')

    return line

@check_form_category()
def attack_form_process(boolean:bool=None, key_word:str=None, *args, **kwargs):
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

def apply_functions(functions:list[Callable], *args, **kwargs):
    for n,f in enumerate(functions):
        match n:
            case 0:
                answer = f(*args, **kwargs)
            case 1:
                line = f(catt_form=answer, *args, **kwargs)
    
    return line

def _level_up_func(iterator:list[list], category:Literal['Level Up']):
    catt = list(map(lambda move: attack_form_process(line=move, location_index=3, category=category), iterator))
    functions.modify_table(iterator,catt)

    return iterator

def level_up_moves(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Level Up']=None):
    scrap_length = len(scrap)
    lines = []
    while start_index < scrap_length:
        line = scrap[start_index:start_index + length]
        lines.append(line)
        start_index += length

    content = _level_up_func(iterator=lines, category=category)

    return content

def tm_tr_move_fix(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None,
        category:Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move',
        'Technical Machine', 'Technical Record', 'Hidden Machine', 'BDSP Technical Machine']=None,
        regional:bool=None):
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

    match regional:
        case True:
            indexes = [3,8,9]
            for idx in indexes:
                line = apply_functions([attack_form_process,obtain_catt_form], line=line, location_index=idx, category=category)

            return line
            
        case _:
            idx = 3
            line = apply_functions([attack_form_process,obtain_catt_form], line=line, location_index=idx, category=category)

            return line

def egg_move_fix(start_index:int, length:int, scrap:list[Tag | NavigableString], category:Literal['Egg Move']=None, regional:bool=None):
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
    def remove_string(to_fix:list[Tag | NavigableString]=None, string:str=None) -> list[Tag | NavigableString]:
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
    line = apply_functions([attack_form_process,obtain_catt_form], line=line, location_index=idx, category=category)

    return line

def move_tutor(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Move Tutor']=None,
        pokemon_name:str=None, regional:bool=None):
    
    line = scrap[start_index:start_index+length]

    if regional:
        indexes = [2,7,8]
        for idx in indexes:
            line = apply_functions([attack_form_process,obtain_catt_form], line=line, location_index=idx, category=category, pokemon_name=pokemon_name)

        return line
    
    idx = 2
    line = apply_functions([attack_form_process,obtain_catt_form], line=line, location_index=idx, category=category, pokemon_name=pokemon_name)

    return line

def special_moves(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Special Move']=None):
    
    idx = 2
    to_fix = scrap[start_index:start_index + length]
    line = apply_functions([attack_form_process,obtain_catt_form], line=to_fix, location_index=idx, index=idx, category=category)

    return line

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

    # If the position has [2,3,4,5,...], then the sum that start from range 1 to 10, will be 4
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

        # Create a new sublist that contains the next value of the line last_element
        sublist = line + [last_element + 1] if len(line) > 1 else line

        # Take a definitive positions for the main_table, the last three (3) or two (2) elements, depending on the length of the list
        final_positions = sublist[2:] if len(sublist) > 3 else sublist[1:] if len(sublist) == 3 else []
        
        # Save the data inside the empty list.
        result.extend(final_positions)

        # Increment the index by the amount of elements that were processed
        index += num

    main_table = functions.eliminate_excess(result,scrap)

    return main_table

def max_z_table_segment(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Z Move','Max Move']=None):
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
    indexes = [2,3,8,9]
    for idx in indexes:
        answer = attack_form_process(line,idx,category)
        if answer == 'N/A' and line_length not in [9,10,11]:
            functions.empty_category_fix(line,idx)
            indexes.remove(idx)
        else:
            line = obtain_catt_form(line=line,location_index=idx,category=category,catt_form=answer)
    
    return line

def pre_evolution_moves(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Pre-evolution']=None, pokemon_name:str=None):
    line = scrap[start_index:start_index + length]
    indexes = [2,7,9] if length > 10 else [2,7]
    for idx in indexes:
        line = apply_functions([attack_form_process,obtain_catt_form], line=line, location_index=idx, category=category, pokemon_name=pokemon_name)

    return line

def transfer_moves(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Transfer']=None, regional_form:bool=None):
    """
    Extracts and processes moves data from a given list of scrap elements.

    Args:
    - scrap (list[Tag | NavigableString], optional): A list of BeautifulSoup Tag or NavigableString elements.
      Defaults to None.
    - category (Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine',
      'Technical Record', 'Hidden Machine', 'Level Up', 'Pre_evolution', 'Egg Move',
      'Move Tutor', 'Transfer'], optional): Specifies the category of moves to filter.
      Defaults to None.
    - regional_form (bool, optional): Specifies whether regional form moves should be included.
      Defaults to None.

    Returns:
    - tuple[list[list], list[list]]: A tuple containing two lists of lists representing moves data:
      1. `moves`: List of lists representing normal moves data.
      2. `r_moves`: List of lists representing regional form moves data.

    This function processes a list of elements (`scrap`) to extract two categories of moves data:
    normal moves and regional form moves. It identifies the start of regional form moves based on
    the presence of the 'Transfer' keyword in the elements. Moves data is extracted and organized
    into tables, with specific keywords used to segment lines of data. Finally, each move's attack
    form is processed and modified in the resulting tables.

    The `make_list` function extracts and separates normal moves and regional moves based on the
    presence of the 'Transfer' keyword.

    The `result_table` function processes a table to extract lines of data based on specified line
    lengths and keywords.

    The `modify_table` function updates the attack form information for each move in the provided tables.

    Example Usage:
    scrap = [BeautifulSoup(Tag), BeautifulSoup(Tag), NavigableString, ...]
    moves, r_moves = transfer_moves(scrap, category='Transfer', regional_form=True)
    # This example extracts and processes moves data for 'Transfers', including regional forms.
    """
    def make_list(regional_form):
        """
        Separates the `scrap` list into normal moves and regional moves based on the presence of
        the 'Transfer' keyword.

        Returns:
        - tuple[list[Tag | NavigableString], list[Tag | NavigableString]]: Two lists of BeautifulSoup
          Tag or NavigableString elements representing normal moves and regional moves respectively.
        """
        moves = scrap
        for number, element in enumerate(scrap):
            if 'Transfer' in str(element):
                regional_list = scrap[number+1:]
                moves = scrap[:number]
                break
        
        if regional_form:
            return moves, regional_list
        
        return moves, None
    
    def result_table(table:list, start_index:int, length:int, keywords:list[str]) -> list[list]:
        """
        Processes a table to extract lines of data based on specified line length and keywords.

        Args:
        - table (list): The table to process.
        - start_index (int): The starting index within the table to begin processing.
        - length (int): The length of each line in the table.
        - keywords (list[str]): Keywords used to identify the end of a line.

        Returns:
        - list[list]: A list of lists representing the processed lines of data.

        Example:
        result = result_table(table, 0, 10, ['Lv.', 'Gen', 'Move Tutor', 'TM'])
        # This example processes a table to extract lines of data ending with specific keywords.
        """
        list_length = len(table)
        content = []
        while start_index < list_length:
            line = table[start_index:start_index + length]
            last_element = line[-1]

            if any(keyword in last_element for keyword in keywords):
                line = table[start_index:start_index + 10]
                start_index += 10
            else:
                start_index += length
            
            content.append(line)
        
        return content
    
    # Calculate the length of moves data based on the provided parameters.
    r_moves = None
    keys = ['Lv.', 'Gen', 'Move Tutor', 'TM']

    # Extract normal moves and regional moves lists.
    normal_moves, regional_moves = make_list(regional_form)
    
    # Process regional moves if they exist.
    if regional_moves:
        r_moves = result_table(table=regional_moves,start_index=start_index,length=length,keywords=keys)
        catt = list(map(lambda move: attack_form_process(line=move, location_index=2, category=category), r_moves))
        functions.modify_table(r_moves,catt)
    
    # Process normal moves.
    moves = result_table(table=normal_moves,start_index=0,length=length,keywords=keys)
    catt = list(map(lambda move: attack_form_process(line=move, location_index=2, category=category), moves))
    functions.modify_table(moves,catt)

    return moves, r_moves