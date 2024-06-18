# Standard libraries of Python
from functools import wraps
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import Callable

def line_elements(index:int=None):
    match index:
        case 2:
            word = ['Physical', 'Other']
        case 3:
            word = 'Special'
        case 8:
            word = ['Normal', 'Alolan', 'Galarian', 'Hisuian', 'Paldean']
        case 9:
            word = ['Alolan', 'Galarian', 'Hisuian', 'Paldean']
    
    return word

def check_word_in_line(func:Callable):
    @wraps(func)
    def wrapper(word:str, line:list[Tag | NavigableString], location_index:int, *args, **kwargs):
        if word_in_line(word,line,location_index):
            return word, True
        
        return func(*args,**kwargs)
    
    return wrapper

def word_in_line(word:str, line:list[Tag | NavigableString], location_index:int) -> bool:
    return word in line[location_index].get('alt', '')

@check_word_in_line
def default_return() -> tuple[str, bool] | tuple[None, bool]:
    return None, False

def check_form_category():
    def decorator(func:Callable):
        @wraps(func)
        def wrapper(line:list[Tag | NavigableString]=None, location_index:int=None, *args, **kwargs) -> str | bool:
            key_word = line_elements(location_index)
            if isinstance(key_word,list):
                for word in key_word:
                    result, flag = default_return(word,line,location_index)
                    if flag:
                        break

            elif isinstance(key_word,str):
                result, flag = default_return(key_word,line,location_index)

            else:
                return 'N/A'
        
            if isinstance(result,str) and result not in ['N/A', 'Physical', 'Special', 'Other']:
                result = result + '_form'
            
            return func(flag,result,*args,**kwargs)
        
        return wrapper
    
    return decorator

def solve_img_issue(regional:bool=None):
    """
    Decorator that apply the same function, changing the string

    Parameter:
    - regional: boolean value that represent the result of another function, in order to know if the pokemon has a regional form.

    Returns:
    - A list containing Tags and NavigableString objects without the column that contain the string.

    Funtions:
    - decorator(func:Callable): This is what activates when you call the decorated function.
        - func: The decorated function.
        - Returns the result of the wraped function.
    - wrapper(line:List[Tag | NavigableString]=None, string:str=None, data_location:int=None, *args, **kwargs): The proper module/function/method that is being decored. in order to process the img problem of the web page Serebii.net of the module that is being decorated.
        - line: segment of the array that needs to be checked.
        - string: text that needs to be eliminated
        - data_location: first point in the line that is being checked.

    """

    def decorator(func:Callable):
        @wraps(func)
        def wrapper(line:list[Tag | NavigableString]=None, string:str=None, data_location:int=None, *args, **kwargs):
            """
            Proper function of the module/function/method that is being decored.
            - line: segment of the array that needs to be checked.
            - string: text that needs to be eliminated
            - data_location: first point in the line that is being checked.
            """

            # Fix the error in Serebii.net html, when it closes the tag of corresponding to regional form img with <img\> in the first element
            html = line[data_location]
            soup = BeautifulSoup(str(html), 'html.parser')

            if regional:
                img_tag = soup.find_all('img')
                if img_tag:
                    forms = [img.get('alt') for img in img_tag]
                    line[data_location] = forms[0]
                    line.insert(8,forms[1])

                result = func(line,string,*args,**kwargs)

                return result
            
            elif not regional:
                img_tag = soup.find('img')
                result = func(tag=img_tag,line=line,*args,**kwargs)

                return result
        
        return wrapper
    
    return decorator