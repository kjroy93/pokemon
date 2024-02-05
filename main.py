# Libraries
from itertools import cycle
from backend.database.src.src import Pokemon,Mega_Pokemon

x = Pokemon(9,'ogerpon')
x.name()
print(x.p_name)
x.elements()
x.weakness()

all_divs = x.soup.find_all('div', attrs={'align': 'center'})
foo_info = all_divs[1].find_all('td', {'class': 'fooinfo'})

mask_abilities = {}
terastallised_abilities = {}

terastallised_cicle = cycle(range(4))

for i in foo_info[10].find_all('b'):
    father = i
    ability = father.text
    if ' Mask ' in ability:
        mask_abilities[ability] = []
        terastallised_abilities[ability] = []
    else:
        continue

for (i, ability) in enumerate(foo_info[10].find_all('b')):
    try:
        father = ability
        ability = father.text

        if ' Mask ' in ability:
            continue

        ability_text = father.next_element.next.strip()
        to_join = [ability, ability_text]
        result = ''.join(to_join)

        if i < 8:
            # Actualizar diccionario mask_abilities
            master_key_index = (i-1) // 2
            mask_key = list(mask_abilities.keys())[master_key_index]
            mask_abilities[mask_key].append(result)
        else:
            # Actualizar diccionario terastallised_abilities
            master_key_index = next(terastallised_cicle)
            terastallised_key = list(terastallised_abilities.keys())[master_key_index]
            terastallised_abilities.setdefault(terastallised_key, []).append(result)

    except TypeError as e:
        print(f'{e}')
        continue


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