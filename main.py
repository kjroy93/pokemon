# Libraries
from backend.database.src.creature import Pokemon,Mega_Pokemon,parse

x = Pokemon(7,6)
x.name()
print(x.p_name)

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

info = []
for i in foo_info[14].find_all('td'):
    info.append(i)

info = info[1:]
org = [item for sublist in info for item in sublist]
reshape = [
    org[i:i+9]
    for i in range(0,len(org),9)
]

reshape = []
i = 0

while i < len(org):
    if i == 0:
        reshape.extend([org[i:i + 9]])
    elif 'The' in org[i + 8].text:
        reshape.extend([org[i:i + 9]])
    else:
        sublist = org[i:i + 8]
        sublist.insert(7, 1)
        reshape.extend([sublist])
        i -= 1

print(reshape)

df = parse.pd_structure(info,quantity_of_columns=8,egg_moves='no')
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