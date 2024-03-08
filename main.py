# Dependencies
import pandas as pd
from bs4 import BeautifulSoup, Tag, NavigableString
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset
from backend.database.src import parse

def normal_regional():
    k = x.p_elements.keys()
    return True if any([i in ['Alolan','Galarian','Hisuian','Paldean'] for i in k]) else False

def regional_case(numerator:int, table:list):
    last_element = 11
    if hasattr(table[numerator+9],'get'):
        return last_element if numerator == 0 or isinstance(table[numerator+9].get('alt',''),str) else 10
    else:
        return last_element - 1

def regional_z_max(numerator:int, table:list):
    last_element = 11
    if hasattr(table[numerator+3],'get'):
        return last_element if numerator == 0 or isinstance(table[numerator+8].get('alt',''),str) else 10
    else:
        return (10 if any(
                word in table[numerator+7].get('alt','')
                for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean', 'Normal'] if not isinstance(
                    table[numerator+7], NavigableString))
            and hasattr(table[numerator+8], 'get') else 9
        ) if len(table) - numerator > 9 else 8

def list_lenght(numerator:int, table:list, limit:str=None):
    regional = normal_regional()
    if not regional:
        last_element = 8
        l = last_element if isinstance(table[numerator+last_element],NavigableString) and table[numerator+last_element] not in ['Gen','Move Tutor','HM'] else 9
    else:
        match limit:
            case 'Z Move' | 'Max Move':
                l = regional_z_max(numerator,table)
            case 'TM' | 'Technical Machine' | 'TR' | 'Technical Record' | 'HM' | 'Hidden Machine':
                l = regional_case(numerator,table)

    def interna():
        return l
    
    return interna

def execution_pass(to_fix:int):
    if to_fix != 11:
        return [2,3,8,9]
    else:
        return True

def is_physical_attack(table,index):
    return any(word in parse.elements_atk(table[index], 1) for word in ['Physical', 'Other'])

def is_special_attack(table,index):
    return any(word in parse.elements_atk(table[index], 1) for word in ['Special'])

def is_normal_form(table,index):
    return any(word in table[index].get('alt','') for word in ['Normal'])

def is_regional_form(table,index):
    return any(word in table[index].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean'])

def category_fix(to_fix:list, index:int, element:bool):
    if index == 2 and not element:
        to_fix.insert(index,'N/A')
    elif index == 3 and isinstance(to_fix[index], NavigableString):
        to_fix.insert(index,'N/A')
    elif index == 8 or index == 9:
        to_fix.insert(index,'N/A')
    else:
        pass

def empty_category_fix(to_fix:list, index:int):
    if index == 2:
        to_fix.insert(index, 'Other')
        to_fix.insert(index+1, 'N/A')
        to_fix.insert(index+2, '--')
    else:
        to_fix.insert(index, 'N/A')

def process_table_segment(start_index:int, length:int, table:list, indexes:list):
    to_fix = table[start_index:start_index+length]
    for idx in indexes:
        if execution_pass(len(to_fix)) == True:
            break
        
        match idx:
            case 2 | 3:
                if not isinstance(to_fix[idx], NavigableString):
                    element = is_physical_attack(to_fix,idx) if idx == 2 else is_special_attack(to_fix,idx)
                    category_fix(to_fix,idx,element)
                else:
                    empty_category_fix(to_fix,idx)
            case 8 | 9:
                element = is_normal_form(to_fix,idx) if idx == 8 else is_regional_form(to_fix,idx)
                category_fix(to_fix,idx,element)
    
    return to_fix
                            
def process_table_recursive(i:int, table:list, limit:str):
    if i >= len(table):
        return []
    
    l = list_lenght(i, table, limit)()
    indexes = execution_pass(l)

    if type(indexes) == list:
        to_fix = process_table_segment(i,l,table,indexes)
        return [to_fix] + process_table_recursive(i+l,table,limit)
    else:
        return [table[i:i+l]] + process_table_recursive(i+l,table,limit)

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

x.name()
x.elements()

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

for i in reversed(result):
    del org[i]

df = process_table_recursive(0,org,'Max Move')

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