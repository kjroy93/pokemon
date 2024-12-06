'''File to scrap the data for the move set, including:
- Level up
- TM & HM
- Move Tutors
- Egg Moves
- Z Moves
- Max Moves
- Transfer Moves'''

# Standard Libraries of Python
from typing import Literal, Callable

# Dependencies
from bs4 import NavigableString, Tag
import pandas as pd
import numpy as np

# Libraries made for this proyect
from backend.database.utils.functions import number_generator, elements_atk, regional_case, regional_z_max, obtain_tuple
from backend.database.parsers.parse_movements import level_up_moves, egg_move_fix, tm_tr_move_fix, move_tutor, special_moves, pre_evolution_moves, transfer_moves
from backend.database.src.creature import Pokemon

class Moveset:
    """
    Represents the moveset information for a given Pokemon.

    Upon initialization, this class initializes various attributes and maps for different categories of movesets,
    based on the Pokemon's generation and potential regional forms.

    Methods:
        - __init__(self, pokemon: Pokemon): Initializes the Moveset object with a Pokemon object,
        initializes necessary attributes, and fetches moveset data from basic tables.
        - __map_population(self, html_section: Tag = None, html_location_info: int = None): Maps and stores location
        information for specific keywords within an HTML section.
        - get_locations(self) -> dict[str | tuple, list[tuple[str, int]]]: Retrieves locations and their respective data
        from an HTML table.
        - __explore_maps(self, category: Literal[...] = None) -> Callable: Determines and returns the appropriate parsing
        function based on the provided category.
        - list_composition(self, location: int = None, category: Literal['Egg Move'] = None) -> list[Tag | NavigableString]:
        Extracts and processes clean components from an HTML table.
        - list_length(self, numerator: int, scrap: list[Tag | NavigableString] = None,
                    category: Literal[...] = None, regional_form: bool = None) -> Literal[8, 9, 10, 11]:
        Determines the number of elements required for a line in the main table based on given parameters.
        - __assign_kwargs(self, category: Literal[...] = None, kwargs: dict = None,
                        regional_form: bool = None): Assigns keyword arguments based on the provided category and regional form.
        - __make_it_table(self, start_index: int = 0, scrap: list[Tag | NavigableString] = None,
                        category: Literal[...] = None, regional_form: bool = None,
                        pokemon_name: str = None, function: Callable = None) -> list[list]:
        Constructs a table of data based on provided parameters and a function.
        - obtain_moves(self, information: str = None, scrap: list[NavigableString | Tag] = None,
                    regional: bool = None): Obtains a list of moves for a Pokémon based on the provided information.

    Notes:
        - The class utilizes BeautifulSoup for HTML parsing and leverages various helper functions for data extraction and processing.
    """

    def __init__(self, pokemon: Pokemon):
        """
        Initializes a Moveset object for a given Pokemon.
        
        Atributtes:
            - pokemon (Pokemon): The Pokemon object for which the moveset information is being managed.
            - _map (dict): A dictionary mapping categories of movesets to corresponding attribute names used for storage.
            - table (BeautifulSoup object): HTML table containing moveset information fetched from the Pokemon's basic tables.
            - lv (list): List to store Level Up moves.
            - lv_form (list): List to store Level Up moves specific to regional forms.
            - tm_hm (list): List to store TM and HM moves.
            - tr (list): List to store TR moves.
            - egg_moves (list): List to store Egg Moves.
            - dynamax (list): List to store Max Moves (Dynamax moves).
            - transfer (list): List to store Transfer moves.
            - transfer_form (list): List to store Transfer moves specific to regional forms.
            - z_moves (list): List to store Z Moves.
            - mt (list): List to store Move Tutor moves.
            - special_movs (list): List to store special moves specific to the Pokemon's generation.
        """
        self.pokemon = pokemon

        # Define categories and corresponding attribute names for movesets
        self.regional_forms = ('Alola', 'Alolan', 'Galar', 'Galarian', 'Hisui', 'Hisuian', 'Paldea', 'Paldean')
        tm_hm = ('TM', 'Technical Machine', 'HM', 'Hidden Machine')
        tr = ('TR', 'Technical Record')
        
        # Map categories to attribute names used for storage
        self._map = {
            'Level Up': ['lv'], self.regional_forms: ['lv_form'], tm_hm: ['tm_hm'], tr: ['tr'],
            'Egg Moves': ['egg_moves'], 'Move Tutor': ['mt'], 'BDSP Move Tutor': ['bdsp_tutor'],
            'BDSP Technical Machine': ['bdsp_tm_hm'], 'Z Moves': ['z_moves'], 'Transfer': ['transfer'],
            'Max Moves': ['dynamax'], 'Pre-Evolution': ['pre_evolution'], 'Special': ['special_movs']
        }

        # Fetch moveset information from basic tables associated with 'moveset' category
        self.table = self.pokemon._basic_tables('moveset')

        # Initialize empty lists for storing movesets of different categories
        self.lv = []
        self.lv_form = []
        self.tm_hm = []
        self.tr = []
        self.egg_moves = []
        self.dynamax = []
        self.transfer = []
        self.transfer_form = []
        self.z_moves = []
        self.mt = []
        self.special_movs = []

        # Conditionally initialize attributes specific to generation 8 Pokemon
        if self.pokemon.gen == 8:
            self.bdsp_tm_hm = []
            self.bdsp_tutor = []
    
    def __map_population(self, html_section: list[Tag] = None, html_location_info: int = None):
        """Maps and stores location information for specific keywords within an HTML section.

        Args:
            html_section (list[Tag], optional): The list of BeautifulSoup Tag objects representing the HTML section to process.
            html_location_info (int, optional): The index or location information associated with the HTML section.

        Returns:
            None: Modifies the internal `_map` dictionary in-place by appending location information for matching keywords.

        Details:
            - Iterates through each keyword-parser pair in the `_map` dictionary.
            - Checks if the keyword exists in the text content of the first element of `html_section`.
            - If a match is found:
                - Appends `html_location_info + 1` to the parser list if the keyword is 'Transfer', otherwise appends `html_location_info`.
                - Stops further iteration using `break` once a match is found.
                - Handles `TypeError` exceptions gracefully during iteration if `html_section[0]` is not accessible.

        Example Usage:
        >>> html_section = soup.find_all('td')
        >>> __map_population(html_section, 3)
        """
        for keyword, parser in self._map.items():
            # Check if parser has not yet been populated
            if len(parser) != 2 or keyword in ['Move Tutor', 'Z Moves', 'Level Up']:
                try:
                    match keyword:
                        case 'Move Tutor' | 'Level Up' | 'Z Moves':
                            if len(parser) < 3 and keyword in html_section[0].text and keyword not in ['Alola', 'Alolan', 'Galar', 'Galarian', 'Hisui', 'Hisuian', 'Paldea', 'Paldean']:
                                # Append location information based on keyword type
                                parser.append(html_location_info)
                                break # Stop further iteration once a match is found
                            else:
                                continue # Continue to the next iteration if the lenght of the list is more than 3
                        
                        case _:
                            # Check if keyword is found in the text content of the first element of html_section
                            if (isinstance(keyword, tuple) and any(key in html_section[0].text for key in keyword)) or (isinstance(keyword, str) and keyword in html_section[0].text):
                                # Append location information based on keyword type
                                parser.append(html_location_info + 1 if keyword == 'Transfer' and self.pokemon.gen == 8 else html_location_info)
                                break  # Stop further iteration once a match is found
                
                except TypeError:
                    continue  # Continue to the next iteration if html_section[0] is not accessible

    def get_locations(self) -> dict[str | tuple, list[tuple[str, int]]]:
        """
        Retrieves locations and their respective data.

        Iterates over positions generated by number_generator and extracts location 
        information from an HTML table. Maps and stores this information in an internal 
        dictionary.

        returns:
            dict[str | tuple, list[tuple[str, int]]]: A dictionary where keys are 
            strings or tuples and values are lists of tuples containing a string 
            and an integer.
        """
        for position in number_generator(8):
            try:
                location = self.table[position].find_all('td')
            except IndexError:
                break

            self.__map_population(location, position)
    
    def __explore_maps(self, category: Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move',
            'Technical Machine', 'Technical Record', 'Hidden Machine', 'Move Tutor',
            'Level Up', 'Pre-evolution', 'Egg Move', 'Transfer'] = None) -> Callable:
        """
        Determines and returns the appropriate parsing function based on the provided category.

        Args:
            category (Literal): Specifies the category of moves or data to be parsed. It can be one of several predefined strings, such as 'TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine', 'Technical Record', 'Hidden Machine',
            'Move Tutor', 'Level Up', 'Pre-evolution', 'Egg Move', or 'Transfer'.

        Returns:
            Callable: The function corresponding to the given category that will be used for parsing.

        Raises:
            AssertionError: If no valid function is found for the provided category.

        Details:
            - Uses a dictionary `f_x_map` where keys are categories and values are corresponding parsing functions.
            - Iterates through `f_x_map` to find a matching function for the provided `category`.
            - If `category` matches any key in `f_x_map`, assigns the corresponding function to `func`.
            - Raises an `AssertionError` if `func` remains `None`, indicating that no valid function was found for `category`.

        Example Usage:
        >>> parser_func = __explore_maps('TM')
        >>> parsed_data = parser_func(html_content)
        >>> print(parsed_data)
        [parsed data based on 'TM' category]
        """
        f_x_map = {
            'Level Up': level_up_moves,
            'Max Move': 1,
            'Egg Move': egg_move_fix,
            ('TM', 'Technical Machine', 'TR',
            'Technical Record', 'HM', 'Hidden Machine'): tm_tr_move_fix,
            'Move Tutor': move_tutor,
            'Special Move': special_moves,
            'Pre-evolution': pre_evolution_moves,
            'Transfer': transfer_moves
        }

        # Identify the correct function to apply based on the category
        func = None
        for key, function in f_x_map.items():
            if (isinstance(key, tuple) and category in key) or (category in key):
                func = function
                break

        assert func is not None, f"No function found for category '{category}'. Please, check the parsers corresponding to parse_movements."

        return func

    def list_composition(self, location: int = None, category: Literal['Egg Move'] = None) -> list[Tag | NavigableString]:
        """
        Extracts and processes clean components from an HTML table represented as a BeautifulSoup object.

        Args:
            location (int, optional): The index of the location in the internal table (`self.table`). Defaults to None.
            category (Literal['Egg Move'], optional): Specifies the category of the data to extract. Defaults to None.

        Returns:
            list(Tag | NavigableString): A list of BeautifulSoup Tag objects and NavigableStrings after filtering and processing.

        Notes:
            Processes an HTML table represented as a BeautifulSoup object (`self.table`). Extracts data from table cells (`td`), and filters out unwanted content like nested tables and line breaks (`<br/>`).
            If `category` is specified as 'Egg Move', it identifies the end of relevant data by checking for the presence of an 'img' tag, and processes the table accordingly using the `egg_move_last_line` helper function.
            `egg_move_last_line` determines the endpoint of content extraction based on specific criteria related to the 'Egg Move' category.

        Example Usage:
        >>> html = BeautifulSoup(html_content, 'html.parser')
        >>> result = list_composition(html, category='Egg Move')
        >>> print(result)
        [Tag1, Tag2, NavigableString1, ...]
        """
        def egg_move_last_line(scrap: list[Tag | NavigableString] = None):
            """
            Determines the index of the last relevant line in the table based on the presence of an 'img' tag.

            Args:
                scrap (list[Union[Tag, NavigableString]]): The list of BeautifulSoup Tag objects and NavigableStrings representing the table.
                It should contain the content extracted from the HTML table.

            Returns:
                int: The index of the last relevant line in the table. If no relevant line is found or 'scrap' is empty,
                it returns -1.

            Notes:
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
            # Divide scrap list into lines, 9 elements per line
            lines = [list(range(i, i + 8)) for i in range(0, len(scrap), 9)]

            for line in lines:
                element = line[-1]
                content = scrap[element]
                # Check if the content contains an 'img' tag
                if content.find('img') is None:
                    break

            return element - 7  # Return the index of the last line

        # Extract initial data from the HTML table
        info = [pos for pos in self.table[location].find_all('td')]
        init_of_data = info[1:]

        # Flatten the initial data into a single list
        scrap = [item for sublist in init_of_data for item in sublist]

        if category == 'Egg Move':
            # Process for 'Egg Move' category
            last_line = egg_move_last_line(scrap)
            content_before = scrap[:last_line]
            content_after = scrap[last_line:]
            # Filter out unwanted content from content_after
            filtered_content_after = list(filter(
                lambda x: all(keyword not in str(x[1]) for keyword in ['table', '<br/>']),
                enumerate(content_after, start=last_line)
            ))
            scrap = content_before + [item[1] for item in filtered_content_after]

        # Process for other categories
        content = list(filter(
            lambda x: all(keyword not in str(x[1]) for keyword in ['table', '<br/>']),
            enumerate(scrap)
        ))
        scrap = list(map(lambda x: x[1], content))

        return scrap  # Return the processed list of BeautifulSoup elements

    def list_length(self, numerator: int, scrap: list[Tag | NavigableString] = None,
            category: Literal['TM', 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine',
                'Technical Record', 'Hidden Machine', 'Level Up', 'Pre-evolution',
                'Egg Move', 'Move Tutor', 'Transfer', 'Special Move'] = None,
            regional_form: bool = None) -> Literal[8, 9, 10, 11]:
        """
        Determines the number of elements required for a line in the main table based on the given category and regional form.

        Args:
            numerator (int): The starting position in the `scrap` list.
            scrap (list[Tag | NavigableString]): The list of HTML tags and strings to process.
            category (Literal): The category to evaluate, affecting the number of elements required.
            regional_form (bool): Indicates if the elements belong to a regional form.

        Returns:
            (int): The number of elements that the line needs to have to be correct in the main table.\n
            Possible values are 8, 9, 10, or 11.

        Raises:
            AssertionError: If the `length` variable remains `None`, indicating an unsupported or invalid `category`.

        Details:
            Determines the appropriate number of elements (`length`) based on the combination of `category` and `regional_form`.
            Supports various categories such as `TM`, 'TR', 'HM', 'Z Move', 'Max Move', 'Technical Machine', 'Technical Record',
            'Hidden Machine', 'Level Up', 'Pre-evolution', 'Egg Move', 'Move Tutor', 'Transfer', and 'Special Move'.
            Special handling for 'Egg Move', 'Z Move', 'Max Move', 'TM', 'TR', 'HM', 'Technical Machine', 'Technical Record',
            'Move Tutor', 'Transfer', 'Pre-evolution', and 'Level Up' categories based on their specific requirements.

        Example Usage:
        >>> length = list_length(0, scrap, 'Egg Move', regional_form=False)
        >>> print(length)
        9
        """
        length = None

        # Determine length based on non-regional forms
        if not regional_form:
            if any(word in category for word in ['Technical Machine', 'Technical Record', 'Hidden Machine', 'Level Up',
                                                'TM', 'TR', 'HM', 'BDSP Technical Machine', 'Move tutor']):
                length = 9
            elif category == 'Pre-evolution':
                length = 10
            elif category == 'Max Move':
                length = 11
            elif category == 'Move Tutor':
                length = 8
            elif category == 'Egg Move':
                data_location = 1
                length = 9 if 'Only' not in scrap[numerator + data_location].text else 10
            else:
                length = 9
            
            return length

        # Determine length based on regional forms using pattern matching
        match category:
            case 'Egg Move':
                data_location = 1
                length = 10 if 'Only' in scrap[numerator + data_location].text or scrap[numerator].text == 'Volt Tackle' else 9
            case 'Z Move' | 'Max Move':
                length = regional_z_max(numerator, scrap)
            case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
                length = regional_case(numerator, scrap, category)
            case 'Move Tutor':
                length = 10
            case 'Transfer':
                length = 9
            case 'Pre-evolution':
                length = regional_case(numerator, scrap, category)
            case 'Level Up':
                length = 9

        # Ensure length is determined; otherwise, raise an AssertionError
        assert length is not None, f"No value associated with category '{category}'. Please check the function `list_length`."

        return length

    def __assign_kwargs(self, category: Literal['Pre-evolution', 'Move Tutor', 'Egg Move', 'Transfer',
                                                'TM', 'TR', 'HM', 'Technical Machine', 'Technical Record'],
        kwargs: dict = None, regional_form: bool = None):
        """
        Assigns keyword arguments (`kwargs`) based on the provided category and regional form flag.

        This method updates the `kwargs` dictionary with specific key-value pairs depending on the
        category of moves or abilities being processed. It optionally includes the regional form flag
        when applicable.

        Args:
            category (Literal): The category of moves or abilities for which keyword arguments are being assigned.
                Should be one of: 'Pre-evolution', 'Move Tutor', 'Egg Move', 'Transfer' 
                'TM', 'TR', 'HM', 'Technical Machine', 'Technical Record'.\n
            kwargs (dict, optional): A dictionary to update with additional keyword arguments. Defaults to None.
            regional_form (bool, optional): Flag indicating whether to consider regional forms. Defaults to None.

        Returns:
            None: Updates the `kwargs` dictionary in place.

        Notes:
            - Depending on the category, specific keyword arguments related to Pokémon name (`pokemon_name`)
            and regional form (`regional`) are added to `kwargs`.
        """
        # Add specific kwargs based on the category
        if category == 'Pre-evolution':
            kwargs.update({'pokemon_name': self.pokemon.p_name})
        elif category == 'Move Tutor':
            kwargs.update({'pokemon_name': self.pokemon.p_name, 'regional': regional_form})
        elif category in ['Egg Move', 'Transfer', 'TM', 'TR', 'HM', 'Technical Machine', 'Technical Record']:
            kwargs.update({'regional': regional_form})

    def __make_it_table(self, start_index: int = 0, scrap: list[Tag | NavigableString] = None,
                        category: Literal['TM', 'TR', 'HM', 'Z Move', 'Level Up',
                                        'Max Move', 'Technical Machine', 'Technical Record', 'Transfer',
                                        'Hidden Machine', 'Pre-evolution', 'Egg Move', 'Move Tutor'] = None,
                        regional_form: bool = None, pokemon_name: str = None, function: Callable = None) -> list[list]:
        """
        Constructs a table of data based on provided parameters and a function.

        This method processes a list of HTML elements (scrap) starting from a specified index (start_index)
        and constructs a table of data based on the category of moves or abilities. It optionally considers
        regional forms of a Pokémon and applies a given function to generate or process the data.

        Args:
            start_index (int, optional): The starting index in the scrap list to begin processing. Defaults to 0.
            scrap (list[Tag | NavigableString], optional): A list of HTML elements or strings to process. Defaults to None.
            category (Literal, optional): The category of moves or abilities to process. Defaults to None.
            regional_form (bool, optional): Flag indicating if regional forms of Pokémon should be considered. Defaults to None.
            pokemon_name (str, optional): The name of the Pokémon, used in processing data. Defaults to None.
            function (Callable, optional): A function to apply for generating or processing data. Defaults to None.

        Returns:
            list[list]: A list representing the constructed table of data. Each element in the outer list represents
            a row in the table, typically a list of strings or processed data elements.

        Notes:
            - If start_index is out of bounds (greater than or equal to the length of scrap), an empty list is returned.
            - The function parameter is expected to handle the processing or generation of data based on provided arguments.
            - Depending on the category, the function may return a single row or recursively build a table of data.
        """
        length = len(scrap)
        if start_index >= length:
            return []

        # Determine the number of elements in the current line to be processed.
        items_in_list = self.list_length(start_index, scrap, category, regional_form)

        # Prepare basic arguments
        args = [start_index, items_in_list, scrap, category]
        kwargs = {}

        # Assign additional keyword arguments based on category and regional_form
        self.__assign_kwargs(category=category, kwargs=kwargs, regional_form=regional_form)

        # Apply the function to process or generate data
        if category in ['Level Up', 'Transfer']:
            line = function(*args, **kwargs)
            return line
        else:
            line = function(*args, **kwargs)

        # Recursively build the table by appending current line and processing subsequent lines
        return [line] + self.__make_it_table(start_index + items_in_list, scrap, category, regional_form, pokemon_name, function)

    def obtain_moves(self, information:str=None, scrap:list[NavigableString | Tag]=None, regional:bool=None):
        """
        Obtains a list of moves for a Pokémon based on the provided information.

        This method retrieves a list of moves for a Pokémon by exploring maps and
        generating a table of move data. If no moves are initially found, an empty
        list is created and the new moves are appended to this list.

        Args:
            information (str, optional): The category of information to explore for moves.
                                        Defaults to None.
            scrap (list[NavigableString | Tag], optional): A list of HTML elements to scrape
                                                        data from. Defaults to None.
            regional (bool, optional): A flag indicating if the regional form of the Pokémon
                                    should be considered. Defaults to None.

        Returns:
            None: This method modifies the internal state by extending the list of moves
                for the Pokémon.
        """

        # Explore the maps with the given category (information) and return a function.
        func = self.__explore_maps(category=information)

        try:
            # Attempt to get the list of moves using the information key from the _map dictionary.
            moves_list = getattr(self, self._map[information][0], None)
        except KeyError:
            # If the information key is not found, obtain a tuple from the _map and use it to get the moves list.
            data = obtain_tuple(information, self._map)
            moves_list = getattr(self, self._map[data][0], None)

        # Generate the content by making a table with the given parameters.
        content = self.__make_it_table(scrap=scrap, category=information, regional_form=regional, pokemon_name=self.pokemon.p_name, function=func)

        # If no moves list was found or created, initialize an empty list.
        if moves_list is None:
            moves_list = []

        # Extend the moves list with the newly generated content.
        moves_list.extend(content)

    def __move_set(self, table:list=None, value:int=None, lenght:int=None, list_name:str=None, atk_type:str=None, form_control:str=None):

        to_populate = getattr(self,list_name)
        to_populate.extend([table[value:value+lenght]])

        for i in to_populate:
            if atk_type == 'Egg Move':
                del i[7]
                i[0] = i[0].text
                i[1] = elements_atk(i[1])
                i[2] = elements_atk(i[2],1)
            
            elif atk_type in ['TM','TR','Technical Machine','Technical Record']:
                i[0] = i[0].text    
                i[1] = i[1].text
                i[2] = elements_atk(i[2])
                i[3] = elements_atk(i[3],1)
            
            else:
                i[1] = i[1].text
                i[2] = elements_atk(i[2])
                i[3] = elements_atk(i[3],1)