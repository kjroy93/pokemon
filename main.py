# Libraries
from backend.database.src.src import Pokemon,Mega_Pokemon,parse

x = Pokemon(7,6)
x.name()
print(x.p_name)

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[0].find_all('table', {'class': 'dextable'})

info = []
for i in foo_info[10].find_all('td'):
    info.append(i)

df = parse.pd_structure(info,quantity_of_columns=8)
print(df)
df = parse.pd_structure(action=1,df=df)
df = parse.pd_structure(action=2,df=df)
print(df)

x.elements()
x.weakness()
x.stats()

try:
    m = Mega_Pokemon(x)
    m.name()
    m.elements()
    m.ability()
    m.weakness()
    m.m_base()
except ValueError as e:
    print(f'{e}')
    

print(x.p_elements)
print(x.p_abilities)
print(x.bases)
# print(x.tauros_types)
# print(x.p_weakness)