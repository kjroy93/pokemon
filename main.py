# Dependencies
import pandas as pd
from bs4 import BeautifulSoup
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.src import parse

x = Pokemon(8,'raichu')
x.name()
print(x.p_name)
x.elements()
x.weakness()
x.stats()

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

info = []
for i in foo_info[17].find_all('td'):
    info.append(i)

data = info[1:]
org = [item for sublist in data for item in sublist]

org = list(filter(lambda x: all(keyword not in str(x[1]) for keyword in ['table', '<br/>']), enumerate(org)))
org = list(map(lambda x: x[1], org))

logs = []

for n,i in enumerate(org):
    try:
        category = parse.elements_atk(i,1)
        logs.append(n) if category is not None else 0
    except (KeyError,TypeError):
        continue

ala = [list(range(i,i+10)) for i in range(1,logs[-1],10)]
hala = [i for i in range(10,logs[-1],10)]
patata = [sum([1 for num in logs if num in group]) for group in ala if sum([1 for num in logs if num in group]) > 0]

result = []
current_index = 0
for i,num in enumerate(patata):
    if num == 1 and patata[i+1] == 3:
        patata[i+1] = 4
        del patata[i]
        num = 4

    sublist = logs[current_index:current_index + num]

    if len(sublist) > 1:
        sublist.append(sublist[-1] + 1)
    else:
        current_index += num
        continue
    
    lst = len(sublist)

    if lst > 3:
        pos = sublist[2:]
    elif lst == 3:
        pos = sublist[1:]
    else:
        continue
    
    result.extend(pos)
    current_index += num

print(result)

for i in reversed(result):
    del org[i]

df = []
i = 0
while i < len(org):
    # Let´s get the primary lenght of the table where the information of the move is located
    if hasattr(org[i+3],'get'):
        l = 11 if i == 0 or isinstance(org[i+8].get('alt',''),str) else 10
    else:
        l = 10 if any(word in org[i+7].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean', 'Normal']) and hasattr(org[i+8],'get') else 9
        
    if l == 11:
        df.extend([org[i:i+l]])
        
    elif l == 10:
        fix = org[i:i+l]

        for i in [1,2,3,8,9]:
            match i:
                case 1:
                    element = any(word in parse.elements_atk(i,1) for word in x.elemental_types)
                    if not element:
                        fix.insert(i, 'N/A')
                case 2 | 3:
                    element = any(word in parse.elements_atk(i) for word in ['Physical', 'Other']) if i == 2 else any(word in parse.elements_atk(i) for word in ['Special'])
                    if not element:
                            fix.insert(i, 'N/A')
                case 7 | 8:
                    element = any(word in fix[i].get('alt','') for word in ['Normal']) if i == 7 else any(['Alolan', 'Galarian', 'Hisuian', 'Paldean'])
                    if not element:
                        fix.insert(i, 'N/A')
        
        df.extend(fix)
    
    elif l == 9:
        fix = org[i:i+l]

        for i in [1,2,3,6,7]:
            match i:
                case 1:
                    element = any(word in parse.elements_atk(i,1) for word in x.elemental_types)
                    if not element:
                        fix.insert(i, 'N/A')
                case 2 | 3:
                    element = any(word in parse.elements_atk(i) for word in ['Physical', 'Other']) if i == 2 else any(word in parse.elements_atk(i) for word in ['Special'])
                    if not element:
                            fix.insert(i, 'N/A')
                case 6 | 7:
                    element = any(word in fix[i].get('alt','') for word in ['Normal']) if i == 6 else any(['Alolan', 'Galarian', 'Hisuian', 'Paldean'])
                    if not element:
                        fix.insert(i, 'N/A')
        
        df.extend(fix)

    i += l

df = pd.DataFrame(df)

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