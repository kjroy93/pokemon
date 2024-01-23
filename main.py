# Libraries
from backend.database.src.src import Pokemon, Mega_Pokemon

x = Pokemon(8,'zacian')
x.name()
print(x.p_name)
x.elements()
x.weakness()
x.abilities()

try:
    m = Mega_Pokemon(x)
    m.elements()
    m.ability()
    m.weakness()
except ValueError as e:
    print(f'Error: {e}')
    

print(x.p_abilities)
print(x.heroes)
print(x.p_weakness)