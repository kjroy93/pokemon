# Libraries
from backend.database.src.src import Pokemon, Mega_Pokemon

x = Pokemon(7,6)
x.name()
x.weakness()
x.elements()

try:
    m = Mega_Pokemon(x)
except ValueError as e:
    print(f'Error: {e}')

m.ability()
print(m.m_abilities)