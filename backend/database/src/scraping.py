

class pokemon():
    def __init__(self, dextable_instance: dextable):
        self.dextable = dextable_instance
        self.elemental_types = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fight', 'Poison', 'Ground', 'Flying', 'Psychc', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']
        self._hit_points = []
        self._atk_points = []
        self._def_ponits = []
        self._sp_atk_points = []
        self._sp_def_points = []
        self._spd_points = []


# def eight_gen():
#     pokedex = pd.DataFrame()
#     for pokemon in pokemons:
#         if pokemon < 100:
#             df = pd.read_html(f'https://www.serebii.net/pokedex-sm/00{pokemon}.shtml')
#         else:
#             df = pd.read_html(f'https://www.serebii.net/pokedex-sm/{pokemon}.shtml')
    
#     name = parse.identity(df)
#     gender = parse.gender(df)
#     weight = parse.weight(df)
#     hab = parse.hab(df)
#     weaknesess = parse.weaknesses(df)
#     egg_group = parse.egg_group(df, len(df))

#     pokedex = pd.concat([pokedex,name,gender,weight,hab,weaknesess,egg_group], ignore_index=True).reset_index(drop=True)

#     print(pokedex)

#     return pokedex