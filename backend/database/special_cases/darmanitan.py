"""class for darmanitan special case"""

# Dependencies
from bs4 import Tag

def darmanitan_types(location:Tag, gen):
    from backend.database.src.src import Pokemon

    if gen < 8:
        strings = ['Normal','Zen Mode']
        darmanitan_types = Pokemon._get_elemental_types(Pokemon,strings,location)

        return darmanitan_types
    
    elif gen >= 8:
        strings = ['Normal','Zen Mode','Galarian']
        darmanitan_types = Pokemon._get_elemental_types(Pokemon,strings,location)
        darmanitan_types['Galarian Zen Mode'] = ['Ice','Fire']

        return darmanitan_types