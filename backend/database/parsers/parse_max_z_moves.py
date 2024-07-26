from bs4 import Tag, NavigableString
from backend.database.utils import functions
from backend.database.parsers.parse_movements import attack_form_process, obtain_catt_form

def obtain_positions(scrap:list[Tag | NavigableString]=None, regional:bool=None):
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
    if regional:
        check_list(group_by, 0, length)
    else:
        check_list(group_by, 0, len(counts))

    return locations, group_by

def get_elements_z_max(groups:list[int]=None, scrap:list[Tag | NavigableString]=None, regional:bool=None,
        gigamax:bool=None, positions:list[int]=None):
    
    inner_dimentions = []
    regional_info = []
    for group in groups:
        dim = sum(inner_dimentions)
        match group:
            case 1:
                if regional:
                    inner_dimentions.append(9)
                    regional_info.append(8)
                elif gigamax:
                    if hasattr(scrap[dim+8],'get'):
                        inner_dimentions.append(10)
                        pos = [7, 8]
                        regional_info.append(pos)
                    elif scrap[dim].text == 'Max Guard':
                        scrap.insert(dim+3, '--')
                        inner_dimentions.append(10)
                        pos = [7, 8]
                        regional_info.append(pos)
                        functions.modify_list(positions,dim+2)
                    else:
                        inner_dimentions.append(8)
                        regional_info.append(7)
                else:
                    inner_dimentions.append(7)
            
            case 2:
                if regional:
                    if hasattr(scrap[dim+8],'get'):
                        inner_dimentions.append(10)
                        regional_info.append(8)
                    else:
                        inner_dimentions.append(12)
                        pos = [9, 10]
                        regional_info.append(pos)
                elif gigamax:
                    if hasattr(scrap[dim+9],'get'):
                        inner_dimentions.append(11)
                        pos = [8, 9]
                        regional_info.append(pos)
                    else:
                        inner_dimentions.append(10)
                        regional_info.append(8)
            
            case 3:
                inner_dimentions.append(13)
                pos = [10, 11]
                regional_info.append(pos)
            
            case 4:
                inner_dimentions.append(14)
                pos = [11, 12]
                regional_info.append(pos)
    
    return inner_dimentions, regional_info

def define_table(groups:list[int]=None, positions:list[int]=None, scrap:list[Tag]=None, regional:bool=None, gigamax:bool=None, *args, **kwargs):
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
    inner_dimentions, regional_info = get_elements_z_max(groups, scrap, regional, gigamax, positions)
    index = 0
    for num in groups:
        indexes = positions[index:index + num]

        scrap = functions.obtain_form_by_index(scrap,indexes,[attack_form_process,obtain_catt_form],modificator='catt',*args,**kwargs)

        # Increment the index by the amount of elements that were processed
        index += num

    result = []
    i = 0
    for n, l in enumerate(inner_dimentions):
        line = scrap[i:i+l]
        if regional:
            line = functions.obtain_form_by_index(line,regional_info[n],func=[attack_form_process,obtain_catt_form],modificator='form',regional=regional,*args,**kwargs)
            
        if gigamax:
            line = functions.obtain_form_by_index(line,regional_info[n],func=[attack_form_process,obtain_catt_form],modificator='form',gigamax=gigamax,*args,**kwargs)
        result.append(line)
        i += l

    return result