from bs4 import Tag, NavigableString
from backend.database.utils import functions
from backend.database.parsers.parse_movements import attack_form_process, obtain_catt_form
from backend.database.parsers.parse_regional import get_regional_form

def get_elements_z_max(scrap:list[Tag | NavigableString]=None, gigamax:bool=None, regional:bool=None, pokemon_name:str=None):
	scrap = functions.elements_atk_catt(scrap, 1)
	if gigamax:
		for pos, element in enumerate(scrap):
			if isinstance(element, Tag):
				try:
					alt_text = element.get('alt', '').lower()
				except KeyError:
					continue

				if alt_text == '':
					continue
				if "gigantamax" in alt_text:
					scrap[pos] = "gigantamax" + f"_{pokemon_name.lower()}"
				elif pokemon_name.lower() in alt_text:
					scrap[pos] = pokemon_name.lower()
				else:
					continue
	# if regional:
	# 	scrap = get_regional_form()
	return (scrap)

def define_table(scrap:list[Tag | NavigableString]=None, pokemon_name:str=None):
	lines = []
	group = []
	pos = 0
	for item in scrap:
		if pos == 3:
			if item.lower() in ['physical', 'special']:
				group.append(item)
			else:
				group.append('N/A')
				if item == '101':
					group.append('N/A')
					pos += 1
				group.append(item)
				pos += 1
		elif pos == 8 and pokemon_name:
			if item == pokemon_name.lower():
				group.append(item)
			else:
				group.append('N/A')
				group.append(item)
				pos += 1
		elif pos == 9 and pokemon_name:
			expected = f"gigantamax_{pokemon_name.lower()}"
			if item == expected:
				group.append(item)
			else:
				group.append('N/A')
				group.append(item)
				pos += 1
		else:
			group.append(item)
		pos += 1

		if pos == 11:
			lines.append(group)
			group = []
			pos = 0