# Dependencies
import pandas as pd

# Libraries
from backend.database.utils import functions
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.parsers import parse_movements
from backend.database.parsers import parse_max_z_moves

# Class test
x = Pokemon(8,'venusaur')

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

x.name()
x.elements()

moveset = Moveset(x)
moveset.get_locations()
scrap = moveset.list_composition(location=moveset._map['Max Moves'][1])
scrap = parse_max_z_moves.get_elements_z_max(scrap, True, pokemon_name=x.p_name)
main_table = parse_max_z_moves.define_table(scrap, x.p_name)
df_1 = pd.DataFrame(main_table)
print(df_1)

try:
	m = Mega_Pokemon(x)
	m.name()
	m.elements()
	m.ability()
	m.weakness()
	m.m_base()
except ValueError as e:
	print(f'{e}')

s = Moveset(x)
s.locations()

for l_type, pos in s._map.items():
	s.make_dataframe(l_type,pos[1])
	
print(x.p_elements)
print(x.p_abilities)
print(x.bases)
# print(x.tauros_types)
# print(x.p_weakness)