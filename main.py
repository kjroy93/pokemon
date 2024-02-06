# Libraries
from backend.database.src.src import Pokemon,Mega_Pokemon

x = Pokemon(9,'ogerpon')
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
    

print(x.p_elements)
print(x.p_abilities)
print(x.bases)
# print(x.tauros_types)
# print(x.p_weakness)