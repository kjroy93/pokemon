# Dependencies
import pandas as pd

# Libraries
from backend.database.utils import functions
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.parsers import parse_movements

# Class test
x = Pokemon(6,6)

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[0].find_all('table', {'class': 'dextable'})

x.name()
x.elements()

moveset = Moveset(x)
moveset.get_locations()
scrap = parse_movements.list_composition(content=foo_info[moveset._map['Level Up'][1]])
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