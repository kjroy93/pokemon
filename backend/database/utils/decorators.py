# Standard libraries of Python
from functools import wraps
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import Callable, Literal

from backend.database.utils.functions import get_dict

def word_in_line(word:str=None, line:list[Tag | NavigableString]=None, location_index:int=None) -> bool:
    """
    Checks if a word is present in the 'alt' attribute of a Tag element at a specific index in the line.

    Parameters:
    - word (str): The word to search for in the 'alt' attribute.
    - line (list[Tag | NavigableString]): A list of BeautifulSoup Tag objects and NavigableStrings.
    - location_index (int): The index in the line where the Tag element is located.

    Returns:
    - bool: True if the word is found in the 'alt' attribute of the Tag at the specified index, False otherwise.
    """
    line_length = len(line)
    if 0 <= location_index < line_length and word is not None:
        element = line[location_index]
        if isinstance(element, Tag):
            try:
                if word in element.get('alt',''):
                    return True
                if word.lower() in element.get('img',''):
                    return True
                if word.lower() in element.get('src',''):
                    return True
                if word.lower() in element.find('img').get('src',''):
                    return True
            except AttributeError:
                pass
            
    return False

def check_word_in_line(func:Callable) -> tuple[None|str, Literal[False, True]]:
    """
    Decorator that checks if a word is present in the 'alt' attribute of a Tag element at a specific index in the line.

    Parameters:
    - func (Callable): The function to be decorated.

    Returns:
    - Callable: The wrapped function that includes the word checking logic.
    """
    @wraps(func)
    def wrapper(word:str=None, line:list[Tag | NavigableString]=None, location_index:int=None, *args, **kwargs) -> tuple[None|str, Literal[False, True]]:
        """
        Wrapper function that checks if a word is present in the 'alt' attribute of a Tag element at a specific index in the line.

        Parameters:
        - word (str): The word to search for.
        - line (list[Tag | NavigableString]): The list of HTML tags and strings to be processed.
        - location_index (int): The index in the line where the Tag element is located.

        Returns:
        - tuple: A tuple containing:
          - str or None: The word processed by the decorated function.
          - bool: True if the word is found and the decorated function executed successfully, False otherwise.
        """
        if word_in_line(word,line,location_index):
            return func(word,location_index,*args,**kwargs)
        
        return None, False
    
    return wrapper

@check_word_in_line
def form_revision(word:str=None, location_index:int=None):
    """
    Determines the form of a move based on the word and location index.

    Parameters:
    - word (str, optional): The word to check.
    - location_index (int, optional): The index in the line to check.

    Returns:
    - tuple: A tuple containing:
    - str or None: The processed word indicating the move form or 'N/A' if not applicable.
    - bool: True if the form is valid, False otherwise.

    Logic:
    - Checks if the word belongs to categories like 'Physical', 'Special', or 'Other'.
    - Returns the word and True if the location index is not 8 or 9.
    - Returns None and False otherwise.
    - Checks if the word belongs to regional forms like 'Alolan', 'Galarian', 'Hisuian', or 'Paldean'.
    - Returns 'N/A' and True if the location index is 8.
    - Returns the word and True otherwise.
    - Returns the word and True by default.
    """
    if word in ['Physical', 'Special', 'Other']:
        if location_index not in [8,9]:
            return word, True
        return None, False
    
    if word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean']:
        if location_index == 8:
            return 'N/A', True
        else:
            return word, True
    
    if word in ['-a', '-g', '-h', '-p']:
        for letter in ['-a', '-g', '-h', '-p']:
            match letter:
                case '-a':
                    word = 'Alola'
                case '-g':
                    word = 'Galar'
                case '-h':
                    word = 'Hisui'
                case '-p':
                    word = 'Paldea'
            break
    
    return word, True

def line_elements(index:int|list=None, pokemon_name:str=None, modificator:str=None,
        regional:bool=None, gigamax:bool=None):
    """
    Determines the valid words for a line element based on the index and category.

    Parameters:
    - index (int, optional): The index in the line to check.
    - category (Literal, optional): The category to evaluate. Possible values include:
        'TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine', 
        'Technical Record', 'Hidden Machine', 'Level Up', 'Pre_evolution', 'Egg Move'.

    Returns:
    - list: A list of valid words for the line element based on the provided index and category.

    Logic:
    - For categories like 'TM', 'TR', 'HM', 'Technical Machine', 'Technical Record',
    'Hidden Machine', 'Level Up', 'Pre_evolution', and 'Egg Move', if the index is 
    not 8 or 9, the function returns a list of general move types: ['Physical', 'Special', 'Other'].
    - For specific indexes, the function returns:
        - Index 2: ['Physical', 'Other']
        - Index 3: ['Special']
        - Index 8: ['Normal', 'Alolan', 'Galarian', 'Hisuian', 'Paldean']
        - Index 9: ['Alolan', 'Galarian', 'Hisuian', 'Paldean']
    """
    if isinstance(index,int):
        if modificator == 'catt' and index not in [7,8,9]:
            word = ['Physical', 'Special', 'Other']

            return word
        
        if modificator == 'form':
            if regional:
                word = ['Normal', 'Alola', '-a', 'Galar', '-g', 'Hisui', '-h', 'Paldea', '-p', pokemon_name]

                return word
            
            elif gigamax:
                word = ['Gigantamax', pokemon_name]

                return word
            
    else:
        assert ValueError(f'(Index must be a integer, but {index} is {type(index)}. Please, check the inputs.)')

def pre_evolution_case(result:str=None, pokemon_name:str=None):
    if result in ['Alola', '-a', 'Galar', '-g', 'Hisui', '-h', 'Paldea', '-p']:
        return 'Learn as ' + pokemon_name + '_' + result, True
    else:
        return 'Learn as ' + pokemon_name, True

def check_form_category():
    """
    Decorator that checks and processes the form category for a line element.

    This decorator wraps a function to include logic for checking and determining the form category
    of a specific element within an HTML table row. It processes different categories like 'TM', 'TR', 
    'HM', 'Z Move', 'Max Move', etc., and modifies the element if necessary.

    Returns:
    - Callable: The wrapped function with additional logic for checking and processing form categories.

    The wrapped function takes the following parameters:
    - line (list[Tag | NavigableString], optional): A list of BeautifulSoup Tag objects and NavigableStrings 
      representing the HTML content.
    - location_index (int, optional): The index in the line where the element is located.
    - category (Literal, optional): The category to evaluate, which can be one of the following:
        'TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine', 'Technical Record', 
        'Hidden Machine', 'Level Up', 'Pre_evolution', 'Egg Move'.
    - *args, **kwargs: Additional arguments and keyword arguments for the wrapped function.

    The wrapped function returns:
    - str | bool: A string representing the processed form category or a boolean flag indicating 
      whether the form category was successfully processed.

    Example:
        @check_form_category()
        def process_form(flag: bool, result: str, *args, **kwargs):
            if flag:
                print(f"Form processed: {result}")
            else:
                print("Form not processed")
        
        line = [...]  # Some list of Tag and NavigableString objects
        process_form(line=line, location_index=3, category='TM')
    """
    def decorator(func:Callable):
        @wraps(func)
        def wrapper(line:list[Tag | NavigableString]=None, location_index:int=None,
            category:Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move',
                'Technical Machine', 'Technical Record', 'Hidden Machine', 
                'Level Up', 'Pre_evolution', 'Egg Move', 'Move Tutor']=None,
            pokemon_name:str=None, *args, **kwargs) -> str | bool:
            
            key_words = line_elements(location_index,pokemon_name,*args,**kwargs)

            if isinstance(key_words,list):
                for word in key_words:
                    result, flag = form_revision(word, line, location_index)
                    if flag:
                        break
                
                if category == 'Pre_evolution':
                    result, flag = pre_evolution_case(result, pokemon_name)

            else:
                return 'N/A'
        
            if isinstance(result,str) and result not in [pokemon_name, 'N/A', 'Physical', 'Special', 'Other', 'Gigantamax'] and 'Learn' not in result:
                result = result + '_form'
            
            return func(flag,result)
        
        return wrapper
    
    return decorator

def solve_img_issue(regional:bool=None) -> list[Tag | NavigableString]:
    """
    Decorator that processes and fixes image issues for regional forms in HTML content.

    This decorator wraps a function to handle and correct image tags related to regional forms 
    in the HTML content. It ensures that the images are processed correctly, especially in cases 
    where the HTML tags might be malformed or improperly closed.

    Parameters:
    - regional (bool, optional): Indicates whether the Pokémon has a regional form. 
      Default is None.

    Returns:
    - Callable: The wrapped function that includes the image processing logic.

    Functions:
    - decorator(func:Callable): The main decorator function that wraps the target function.
    - wrapper(line:list[Tag | NavigableString]=None, string:str=None, data_location:int=None, *args, **kwargs):
        The function that processes the image issues.

        Parameters:
        - line (list[Tag | NavigableString], optional): The segment of the array that needs to be checked.
        - string (str, optional): The text to be eliminated.
        - data_location (int, optional): The starting point in the line that is being checked.

        Returns:
        - The result of the decorated function after processing the image issues.

    Example:
        @solve_img_issue(regional=True)
        def process_images(line, string, data_location):
            # Function logic here
            return line
        
        line = [...]  # Some list of Tag and NavigableString objects
        process_images(line=line, string='Details', data_location=8)
    """
    def decorator(func:Callable):
        @wraps(func)
        def wrapper(line:list[Tag | NavigableString]=None, string:str=None, data_location:int=None, *args, **kwargs):
            """
            Processes and fixes image issues for regional forms in the HTML content.

            Parameters:
            - line (list[Tag | NavigableString]): The segment of the array that needs to be checked.
            - string (str, optional): The text to be eliminated.
            - data_location (int, optional): The starting point in the line that is being checked.

            Returns:
            - Result of the decorated function after processing the image issues.
            """
            # Fix the error in Serebii.net html, when it closes the tag of corresponding to regional form img with <img\> in the first element
            html = line[data_location]
            soup = BeautifulSoup(str(html), 'html.parser')

            if regional:
                img_tag = soup.find_all('img')
                if img_tag:
                    forms = [img.get('alt') for img in img_tag]

                    second_form = forms[1].split()
                    form = second_form[0] + '_' + second_form[1]
                    del forms [1]
                    forms.append(form)

                    line[data_location] = forms[0]
                    line.insert(8,forms[1])

                result = func(line,string,*args,**kwargs)

                return result
            
            elif not regional:
                result = func(line,string,*args,**kwargs)

                return result
        
        return wrapper
    
    return decorator

def catt_form_logic():
    """
    Decorator that processes the category form logic for a line element.

    This decorator wraps a function to handle and process category form logic 
    for elements in a line. It checks the category and form type, ensuring that the 
    appropriate logic is applied based on the category and index.

    Returns:
    - Callable: The wrapped function that includes the category form logic.

    Functions:
    - decorator(func:Callable): The main decorator function that wraps the target function.
    - wrapper(index:int=None, catt_form:str=None, category:Literal[
                'TM', 'TR', 'HM', 'Z Move', 'Max Move',
                'Technical Machine', 'Technical Record', 'Hidden Machine', 
                'Level Up', 'Pre_evolution', 'Egg Move', Move Tutor]=None, 
              line:list[Tag | NavigableString]=None, *args, **kwargs):
        The function that processes the category form logic.

        Parameters:
        - index (int, optional): The index in the line to check.
        - catt_form (str, optional): The form category to be processed.
        - category (Literal, optional): The category to evaluate.
        - line (list[Tag | NavigableString], optional): A list of BeautifulSoup Tag objects and NavigableStrings.

        Returns:
        - The result of the decorated function after processing the category form logic.

    Example:
        @catt_form_logic()
        def process_category_form(answer, line, index, catt_form):
            # Function logic here
            return line
        
        line = [...]  # Some list of Tag and NavigableString objects
        process_category_form(index=3, catt_form='Physical', category='TM', line=line)
    """
    def decorator(func:Callable):
        """
        Processes the category form logic for a line element.

        Parameters:
        - index (int, optional): The index in the line to check.
        - catt_form (str, optional): The form category to be processed.
        - category (Literal, optional): The category to evaluate.
        - line (list[Tag | NavigableString], optional): A list of BeautifulSoup Tag objects and NavigableStrings.

        Returns:
        - The result of the decorated function after processing the category form logic.
        """
        @wraps(func)
        def wrapper(location_index:int=None, catt_form:str=None,
            category:Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine',
                'Technical Record', 'Hidden Machine', 'Level Up',
                'Pre-evolution', 'Egg Move', 'Move Tutor', 'Transfer Move']=None,
            line:list[Tag | NavigableString]=None, pokemon_name:str=None, *args, **kwargs) -> list[Tag | NavigableString]:
            """
            Processes the category form logic for a line element.

            Parameters:
            - index (int, optional): The index in the line to check.
            - catt_form (str, optional): The form category to be processed.
            - category (Literal, optional): The category to evaluate.
            - line (list[Tag | NavigableString], optional): A list of BeautifulSoup Tag objects and NavigableStrings.

            Returns:
            - The result of the decorated function after processing the category form logic.
            """
            answer = None
            
            catt_dict = get_dict(pokemon_name,category)
            
            for i in catt_dict.keys():
                if any(word == catt_form for word in catt_dict[i]):
                    answer = True
                    break
            
            if 'Learn' in catt_form:
                answer = True

            result = func(answer,line,location_index,catt_form,pokemon_name=pokemon_name,*args,**kwargs)

            return result
        
        return wrapper
    
    return decorator