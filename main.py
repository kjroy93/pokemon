# Dependencies
import pandas as pd
from bs4 import BeautifulSoup, Tag, NavigableString
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.parsers import parse_movements

x = Pokemon(8,'raichu')
x.name()
print(x.p_name)
x.elements()
x.weakness()
x.stats()

# Egg moves in case of regional form pokémon, for the 8th generation and 7th generation, including BDSP data
# Class test

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

x.name()

scrap = parse_movements.list_composition(table=foo_info[15],category='Egg Move')
regional = parse_movements.normal_regional(x.p_elements)
table = parse_movements.process_table_recursive(0,scrap,'Egg Move',regional_form=regional,category='Egg Move')

print(table)


# form_egg_moves = scrap[0:reference[0]]
# eightgen_egg_moves = scrap[reference[0]:reference[1]]
# bdsp_egg_moves = scrap[reference[1]:reference[2]]

# form_egg_moves = pd.DataFrame([scrap[i:i+10] for i in range(0,reference[0],10)])
# eightgen_egg_moves = pd.DataFrame([scrap[i:i+8] for i in range(reference[0],reference[1],8)])
# bdsp_egg_moves = pd.DataFrame([scrap[i:i+7] for i in range(reference[1],reference[2],7)])

# if exclusive_move_case:
#     exclusive_move_case = pd.DataFrame([exclusive_move_case])
#     eightgen_egg_moves = pd.concat([eightgen_egg_moves,exclusive_move_case], ignore_index=True)
# bdsp_egg_moves[9] = bdsp_egg_moves[1]
# bdsp_egg_moves = bdsp_egg_moves.drop(columns=1)
# bdsp_egg_moves.columns = range(len(bdsp_egg_moves.columns))
# eightgen_egg_moves = pd.concat([eightgen_egg_moves,bdsp_egg_moves], axis=0, ignore_index=True)

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