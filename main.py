# Dependencies
import pandas as pd

# Libraries
from backend.database.utils import functions
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.parsers import parse_movements
from backend.database.parsers.parse_movements import attack_form_process

# Class test
x = Pokemon(8,'charizard')

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

x.name()
x.elements()

# Move Tutor attacks scrap
scrap = parse_movements.list_composition(html=foo_info[14])
regional = functions.normal_regional(x.p_elements)
df = parse_movements.make_it_table(scrap=scrap,category='Move Tutor',regional_form=regional,pokemon_name=x.p_name)

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