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

# Max Moves and Z Moves data scrap from Serebii.net, for pokemon with regional forms
# Class test
x = Pokemon(8,'raichu')

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

scrap = parse_movements.list_composition(foo_info[17])
positions, group = parse_movements.obtain_positions(scrap)

result = []
index = 0
for num in group:
    line = positions[index:index+num]
    last_element = line[-1]
    length = len(line)

    line = line + [last_element + 1] if len(line) > 1 else line
    pos = line[2:] if length > 3 else line[1:] if length == 3 else []
    
    result.extend(pos)
    index += num

main_table = parse_movements.eliminate_excess(result,scrap)
df = parse_movements.process_table_recursive(0,main_table,'Max Move',x.p_elements)

print(pd.DataFrame(df))

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