# Dependencies
import pandas as pd

# Libraries
from backend.database.utils import functions
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.parsers import parse_movements
from backend.database.parsers import parse_max_z_moves

# Class test
x = Pokemon(8,'charizard')

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

x.name()
x.elements()

moveset = Moveset(x)
moveset.get_locations()
print(moveset._map)
scrap = moveset.list_composition(location=moveset._map['Max Moves'][1])
positions, group = parse_max_z_moves.obtain_positions(scrap)
main_table = parse_max_z_moves.define_table(group,positions,scrap,gigamax=True,pokemon_name=x.p_name)
print(main_table)

moveset.obtain_moves(information='Level Up',scrap=scrap,regional=True)
print(moveset.lv)

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