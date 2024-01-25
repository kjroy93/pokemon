"class for urshifu special case"

# Dependencies
from bs4 import Tag

def urshifu_styles(location:Tag):
    from backend.database.src.src import Pokemon
    styles = location.text

    first_style = styles[0:19]
    second_style = styles[20:38]

    styles = [first_style,second_style]

    urshifu_types = Pokemon._get_elemental_types(Pokemon,styles,location)

    return urshifu_types