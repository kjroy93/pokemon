"""
Module for handling specific functionalities related to Calyrex in a game database.

This module provides functions to retrieve types and weaknesses of Calyrex and its forms.

Functions:
- calyrex_types(location: Tag) -> list: Retrieves elemental types of Calyrex and its forms based on provided location data.
- calyrex_weakness(location: Tag, elemental_types: list) -> tuple: Retrieves weaknesses of Calyrex and its specific forms based on provided elemental types and location data.
"""

# Dependencies
from bs4 import Tag

def calyrex_types(location:Tag):
    """
    Retrieves the elemental types of Calyrex and its different forms based on the provided location data.

    This function parses the text content from the given BeautifulSoup Tag object (location) to extract
    the names of Calyrex and its forms. It then retrieves the elemental types associated with each of 
    these forms using a database query method.

    Args:
    - location (Tag): A BeautifulSoup Tag object containing the relevant data for Calyrex and its forms.

    Returns:
    - list: A list of elemental types corresponding to Calyrex and its forms.
    Each element in the list represents the elemental type(s) associated with a specific form of Calyrex.

    Raises:
    - ImportError: If the backend.database.src.creature.Pokemon module cannot be imported.

    Note:
    This function assumes a specific format for the text content within the provided location Tag,
    where the first word represents Calyrex and subsequent words represent its different forms.
    """
    from backend.database.src.creature import Pokemon

    text = location.text.strip().split()
    forms = [f'{text[i]} {text[i+1]}' for i in range(1,len(text),2)]
    calyrex_t = text.pop(0)
    calyrex = [calyrex_t] + forms

    calyrex_types = Pokemon._get_elemental_types(Pokemon,calyrex,location,'calyrex')

    return calyrex_types

def calyrex_weakness(location:Tag, elemental_types:list):
    """
    Retrieves the weaknesses of Calyrex and its specific forms (Calyrex Ice Rider and Calyrex Shadow Rider)
    based on the provided elemental types and location data.

    This function extracts specific segments (values) from the given BeautifulSoup Tag object (location) to
    identify the weaknesses associated with Calyrex, Calyrex Ice Rider, and Calyrex Shadow Rider. Each segment
    of values corresponds to 18 characters representing weaknesses for each respective form.

    Args:
    - location (Tag): A BeautifulSoup Tag object containing relevant data for weaknesses.
    - elemental_types (list): A list of elemental types affecting Calyrex.

    Returns:
    - tuple: A tuple containing weaknesses for Calyrex, Calyrex Ice Rider, and Calyrex Shadow Rider.
    Each element in the tuple is a list of weaknesses corresponding to the respective form.

    Raises:
    - ImportError: If the backend.database.src.creature.Pokemon module cannot be imported.

    Note:
    This function assumes that the weaknesses are extracted from specific segments of the provided location Tag
    object. Each segment represents weaknesses for Calyrex, Calyrex Ice Rider, and Calyrex Shadow Rider,
    respectively, in a predetermined format.
    """
    from backend.database.src.creature import Pokemon

    values = location[18:]

    calyrex = values[0:18]
    calyrex_ice = values[18:36]
    calyrex_shadow = values[36:54]

    calyrex_weakness = Pokemon._get_list_of_weakness(Pokemon,'calyrex',None,elemental_types,calyrex)
    calyrex_i_weakness = Pokemon._get_list_of_weakness(Pokemon,'calyrex',None,elemental_types,calyrex_ice)
    calyrex_s_weakness = Pokemon._get_list_of_weakness(Pokemon,'calyrex',None,elemental_types,calyrex_shadow)

    return calyrex_weakness,calyrex_i_weakness,calyrex_s_weakness