# Libraries
from backend.database.src.creature import Pokemon,Mega_Pokemon
from backend.database.src.moveset import Moveset

x = Pokemon(8,'raichu')
x.name()
print(x.p_name)
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

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('table', {'class': 'dextable'})

info = []
for i in foo_info[12].find_all('td'):
    info.append(i)

to_fill = []
to_delete = []

# Suponiendo que `foo_info[12]` contiene la lista de elementos td que proporcionaste
for n, td_element in enumerate(info):
    skip_row = True
    try:
        pkmn_elements = td_element.find_all(class_='pkmn')

        for pkmn in pkmn_elements:
            if skip_row:
                e = n
                to_delete.append(e)
                skip_row = False

            img_element = pkmn.find('img')
            n += 1

            if img_element:
                alt_text = img_element.get('alt', 'No alt text')
                del info[n]
                info.insert(n,alt_text)
                
    except AttributeError:
        pass

for idx in reversed(to_delete):
    del info[idx]

data = info[1:]

i = 0
while i < len(data):
    l = 11 if i == 0 or isinstance(data[i+9],str) else 10
    if l == 10 and any(word in data[i+8] for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean']):
        fix = data[i:i+l]
        fix.insert(8, 'N/A')
        to_fill.extend(fix)
    else:
        to_fill.extend([data[i:i+l]])
    i += l 

    print(i)

s = Moveset(x)
s.locations()

for l_type, pos in s._map.items():
    s.make_dataframe(l_type,pos[1])
    
print(x.p_elements)
print(x.p_abilities)
print(x.bases)
# print(x.tauros_types)
# print(x.p_weakness)