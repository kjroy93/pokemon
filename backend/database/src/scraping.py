# Standard libraries of Python

from time import gmtime

# Dependencies
import pandas as pd
import requests
from pandas import DataFrame

from backend.database.src import parse

assert requests.get("https://www.serebii.net/index2.shtml").status_code == 200, 'There is a problem with Euromillions webpage'

pokemons = range(1,3)

def eight_gen():
    pokedex = pd.DataFrame()
    for pokemon in pokemons:
        if pokemon < 100:
            df = pd.read_html(f'https://www.serebii.net/pokedex-sm/00{pokemon}.shtml')
        else:
            df = pd.read_html(f'https://www.serebii.net/pokedex-sm/{pokemon}.shtml')
    
    name = parse.identity(df)
    gender = parse.gender(df)
    weight = parse.weight(df)
    hab = parse.hab(df)
    weaknesess = parse.weaknesses(df)
    egg_group = parse.egg_group(df, len(df))

    pokedex = pd.concat([pokedex,name,gender,weight,hab,weaknesess,egg_group], ignore_index=True).reset_index(drop=True)

    print(pokedex)

    return pokedex