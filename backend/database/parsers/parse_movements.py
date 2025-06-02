# Standard libraries of Python
from typing import Literal, Callable

# Dependencies
from bs4 import NavigableString, Tag

# Libraries
from backend.database.utils.functions import apply_functions, modify_table, remove_string
from backend.database.utils.decorators import solve_img_issue, check_form_category, catt_form_logic

@catt_form_logic()
def obtain_catt_form(answer:bool|str=None, line:list[Tag | NavigableString]=None, idx:int=None, catt_form:str|bool=None,
		modificator:bool=None, pokemon_name:str=None, gigamax:str=None):
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
		match modificator:
			case 'catt':
				line[idx] = catt_form.lower()
				return line

			case 'form':
				if catt_form not in ['Normal_form', 'Alola_form', 'Alolan_form', 'Galarian_form', 'Hisuian_form', 'Paldean_form'] and idx not in [2,3]:
					line[idx] = 'normal_form'
					return line
				
				else:
					line[idx] = catt_form.lower()
					return line
	
	elif isinstance(answer,str) or not answer:
		line.insert(idx,'N/A')
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

def _level_up_func(iterator:list[list], category:Literal['Level Up']):
	catt = list(map(lambda move: attack_form_process(line=move, location_index=3, category=category), iterator))
	modify_table(iterator,catt)

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

def pre_evolution_moves(start_index:int=None, length:int=None, scrap:list[Tag | NavigableString]=None, category:Literal['Pre-evolution']=None):
	line = scrap[start_index:start_index + length]
	indexes = [2,7,9] if length > 10 else [2,7]
	for idx in indexes:
		pokemon_name = line[idx].find('img').get('src')
		pokemon_name = remove_string([pokemon_name])
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
		modify_table(r_moves,catt)
	
	# Process normal moves.
	moves = result_table(table=normal_moves,start_index=0,length=length,keywords=keys)
	catt = list(map(lambda move: attack_form_process(line=move, location_index=2, category=category), moves))
	modify_table(moves,catt)

	return moves, r_moves