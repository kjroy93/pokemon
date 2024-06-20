# Dependencies
from bs4 import Tag, ResultSet, NavigableString

def number_generator(init:int):
    """
    Generates a sequence of numbers starting from `init` up to 999.

    This generator function yields numbers sequentially starting from the specified initial number
    up to 1999. It continues generating numbers indefinitely until the upper limit is reached.

    Parameters:
    - init (int): The starting number for the generator.

    Yields:
    - int: The next number in the sequence starting from `init` up to 999.
    """
    for number in range(init,2000):
        yield number
    
def remove_string(data:list[str]):
    """
    Removes specified substrings from each element in the list `data`.

    Parameters:
    - data (list[str]): A list of strings where substrings will be removed.

    Returns:
    - list[str]: The list with specified substrings removed from each element.
    """
    words = 'Attacking Move Type: ','-type'
    for string in words:
        data = list(map(lambda x: x.replace(string,''),data))

    return data

def make_dict(elemental:list, v:list):
    """
    Creates a dictionary from two lists `elemental` and `v`.

    Parameters:
    - elemental (list): List of keys.
    - v (list): List of values.

    Returns:
    - dict: A dictionary where each key-value pair is derived from `elemental` and `v`.
    """
    return dict(zip(elemental,v))

def eliminate_excess(positions:list[int], scrap:list[Tag | NavigableString]):
    """
    Removes elements from `scrap` based on their indices provided in `positions`.

    This function filters out elements from the `scrap` list based on the specified indices
    in `positions`. It returns a new list containing elements from `scrap` except those at
    indices specified in `positions`.

    Parameters:
    - positions (list[int]): Indices of elements to be removed from `scrap`.
    - scrap (list[Tag | NavigableString]): A list of BeautifulSoup Tag objects and NavigableStrings.

    Returns:
    - list[Tag | NavigableString]: Filtered list of elements from `scrap`, excluding those at indices in `positions`.
    """

    return [element for idx, element in enumerate(scrap) if idx not in positions]

def empty_category_fix(to_fix:list[Tag | NavigableString]=None, index:int=None):
    """
    Fixes empty category entries in the list `to_fix` at the specified `index`.

    Parameters:
    - to_fix (list[Tag | NavigableString], optional): The list to be fixed.
    - index (int, optional): The index where fixes are applied.

    Modifies `to_fix` in-place.
    """
    if index == 2:
        to_fix.insert(index, 'Other')
        to_fix.insert(index+1, 'N/A')
        to_fix.insert(index+2, '--')
    else:
        to_fix.insert(index, 'N/A')

def normal_regional(pokemon_ability:dict | list):
    """
    Checks if `pokemon_ability` indicates a regional variant.

    Parameters:
    - pokemon_ability (dict | list): Either a dictionary or a list representing Pokémon abilities.

    Returns:
    - bool: True if `pokemon_ability` contains regional variants ('Alolan', 'Galarian', 'Hisuian', 'Paldean'), False otherwise.
    """
    if isinstance(pokemon_ability,dict):
        k = pokemon_ability.keys()
        return True if any([i in ['Alolan','Galarian','Hisuian','Paldean'] for i in k]) else False
    elif isinstance(pokemon_ability,list):
        return False

def regional_case(numerator:int, scrap:list[Tag]):
    """
    Determines the index of the last relevant element for regional cases in a list of BeautifulSoup Tag objects.

    This function checks if a specific condition is met in the `scrap` list starting from the `numerator` index.
    If the condition is satisfied, it returns 11. Otherwise, it returns 10 if `numerator` is 0 or the condition
    isn't met at `scrap[numerator+9]`; otherwise, it returns 10.

    Parameters:
    - numerator (int): The starting index to check within the `scrap` list.
    - scrap (list[Tag]): A list of BeautifulSoup Tag objects representing the data.

    Returns:
    - int: The index of the last relevant element based on the conditions.
    """
    last_element = 11
    if hasattr(scrap[numerator+9],'get'):
        return last_element if numerator == 0 or isinstance(scrap[numerator+9].get('alt',''),str) else 10
    else:
        return last_element - 1

def regional_z_max(numerator:int, scrap:list[Tag]):
    """
    Determines the index of the last relevant element for regional Z-Max cases in a list of BeautifulSoup Tag objects.

    This function checks specific conditions in the `scrap` list starting from the `numerator` index to determine
    the index of the last relevant element. If certain conditions are met, it returns 11. Otherwise, it evaluates
    further conditions to decide between returning 10 or 9 based on the presence of specific attributes and values
    in the `scrap` list.

    Parameters:
    - numerator (int): The starting index to check within the `scrap` list.
    - scrap (list[Tag]): A list of BeautifulSoup Tag objects representing the data.

    Returns:
    - int: The index of the last relevant element based on the conditions.
    """
    last_element = 11
    if hasattr(scrap[numerator+3],'get'):
        return last_element if numerator == 0 or isinstance(scrap[numerator+8].get('alt',''),str) else 10
    else:
        return (10 if any(
                word in scrap[numerator+7].get('alt','')
                for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean', 'Normal'] if not isinstance(
                    scrap[numerator+7], NavigableString
                )
            ) and hasattr(scrap[numerator+8], 'get') else 9
        ) if len(scrap) - numerator > 9 else 8

def elements_atk(a_tag:Tag, control:int=None):
    """
    Extracts the attacking move type from an <img> tag's 'src' attribute based on control settings.

    The function checks the 'src' attribute of the provided BeautifulSoup Tag (`a_tag`) to determine
    the attacking move type based on the `control` parameter. It supports extracting elemental types
    ('Normal', 'Fire', 'Water', etc.) or attack categories ('physical', 'special', 'other').

    Parameters:
    - a_tag (Tag): The BeautifulSoup Tag object representing the <img> tag.
    - control (int, optional): Specifies the type of information to extract:
        - None: Returns the elemental type in capitalized form ('Fire', 'Water', etc.).
        - 1: Returns the attack category in lowercase ('physical', 'special', 'other').
    
    Returns:
    - str or None: Depending on the `control` setting, returns the attacking move type or None if not found.

    Raises:
    - ValueError: If `control` is provided and not equal to 1.

    Notes:
    - The 'src' attribute of `a_tag` should contain relevant information about the attacking move type.
    - For elemental types, it matches substrings in lowercase within the 'src' attribute.
    - For attack categories, it directly compares lowercase strings.

    Example:
    >>> img_tag = BeautifulSoup('<img src="https://example.com/fire.png">', 'html.parser').find('img')
    >>> elements_atk(img_tag)  # Returns 'Fire'
    >>> elements_atk(img_tag, 1)  # Returns 'physical'
    """
    elemental_types = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
        'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
    ]

    category = [
        'physical', 'special', 'other'
    ]

    minus = [elemental_type.lower() for elemental_type in elemental_types]

    if control == None:
        text = minus
    elif control == 1:
        text = category
    else:
        raise ValueError('The Control variable must be 1 if you want to process atk types')

    for n,i in enumerate(text):
        type_text = a_tag['src']
        if i in type_text:
            return str(text[n].capitalize())

def list_of_elements(location:ResultSet[Tag]):
    """
    Extracts a list of clean element types from a BeautifulSoup ResultSet of Tags.

    This function iterates through the first 18 elements of the provided ResultSet (`location`), 
    which typically represents a collection of HTML tags. It searches for <img> tags within each 
    element to extract the 'alt' attribute. If the 'alt' attribute is missing, it uses the 
    `elements_atk` function to determine the attacking move type from the <img> tag's 'src' attribute.

    Parameters:
    - location (ResultSet[Tag]): The BeautifulSoup ResultSet containing Tag elements.

    Returns:
    - list[str]: A list of clean element types extracted from the ResultSet after processing.

    Notes:
    - The function limits processing to the first 18 elements of `location`.
    - It handles cases where 'alt' attributes are missing by using `elements_atk` to infer the type.
    - Uses `remove_string` function to clean up extraneous text from the extracted types.

    Example:
    >>> result_set = BeautifulSoup(html_content, 'html.parser').find_all('td')
    >>> list_of_elements(result_set)  # Returns a list of cleaned element types
    """
    types = []
    location = location[0:18]

    for tag in location:
        a_tag = tag.find('img')
        if a_tag and not isinstance(a_tag,Tag):
            continue

        try:
            type_text = a_tag['alt']
            types.append(type_text)
        except KeyError:
            type_text = elements_atk(a_tag)
            types.append(type_text)
    
    types = remove_string(types)
    
    return types

def search_text(main_table:list[Tag], text:str):
    for table in main_table:
        if table[0].text == text:
            return table
        else:
            pass