# Dependencies
import pandas as pd

# Libraries
from backend.database.utils import functions
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.parsers import parse_movements

# Class test
x = Pokemon(8,'raichu')

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

x.name()
x.elements()

# TM | TR | Technical Machine | Technical Record case for regional form pokémon in the 8th generation and 7th generation
scrap = parse_movements.list_composition(foo_info[12])
regional = functions.normal_regional(x.p_elements)
df = parse_movements.make_it_table(start_index=264,scrap=scrap,category='TM',regional_form=regional)

pd.DataFrame(df)

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