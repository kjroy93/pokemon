"class for urshifu special case"

# Dependencies
from bs4 import Tag

def urshifu_styles(location:Tag):
    from backend.database.src.creature import Pokemon
    styles = location.text

    first_style = styles[0:19]
    second_style = styles[20:38]

    styles = [first_style,second_style]

    urshifu_types = Pokemon._get_elemental_types(Pokemon,styles,location,'urshifu')

    return urshifu_types

def urshifu_weakness(location:Tag, elemental_types:list):
    from backend.database.src.creature import Pokemon

    values = location[18:]

    single_strike = values[0:18]
    rapid_strike = values[18:36]

    single_strike_weakness = Pokemon._get_list_of_weakness(Pokemon,'urshifu',None,elemental_types,single_strike)
    rapid_strike_wekaness = Pokemon._get_list_of_weakness(Pokemon,'urshifu',None,elemental_types,rapid_strike)

    return single_strike_weakness,rapid_strike_wekaness