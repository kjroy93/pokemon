'''File to scrap the data for the move set, including:
- Level up
- TM & HM
- Move Tutors
- Egg Moves
- Z Moves
- Max Moves
- Transfer Moves'''

# Standard Libraries of Python
from typing import Tuple, Literal, Generator

# Dependencies
from bs4 import NavigableString, Tag
import pandas as pd
import numpy as np

# Libraries made for this proyect
from backend.database.utils.functions import number_generator, elements_atk
from backend.database.parsers.parse_movements import explore_maps, make_it_table
from backend.database.src.creature import Pokemon

class Moveset():
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon

        regional_forms = ('Alola', 'Alolan', 'Galar', 'Galarian', 'Hisui', 'Hisuian', 'Paldea', 'Paldean')
        tm_hm = ('TM', 'Technical Machine', 'HM', 'Hidden Machine')
        tr = ('TR', 'Technical Record')
        self._map = {
            'Level Up': ['lv'], regional_forms: ['lv_form'], tm_hm: ['tm_hm'], tr: ['tr'],
            'Egg Moves': ['egg_moves'], 'Move Tutor': ['mt'], 'BDSP Move Tutor': ['bdsp_tutor'], 'BDSP Technical Machine': ['bdsp_tm_hm'],
            'Z Moves': ['z_moves'], 'Transfer': ['transfer'], 'Max Moves': ['dynamax'], 'Pre-Evolution': ['pre_evolution']
        }

        self.table = self.pokemon._basic_tables('moveset')

        self.lv = []
        self.lv_form = []
        self.tm_hm = []
        self.tr = []
        self.egg_moves = []
        self.dynamax = []
        self.transfer = []
        self.transfer_form = []
        self.z_moves = []
        self.mt = []
        self.special_movs = []

        if self.pokemon.gen == 8:
            self.bdsp_tm_hm = []
            self.bdsp_tutor = []
    
    def __map_population(self, html_section:Tag=None, html_location_info:int=None):
        for keyword, p_list in self._map.items():
            if len(p_list) != 2:
                try:
                    if (isinstance(keyword, tuple) and any(key in html_section[0].text for key in keyword)) or (isinstance(keyword, str) and keyword in html_section[0].text):
                        p_list.append(html_location_info + 1 if keyword == 'Transfer' else html_location_info)
                        break
                except TypeError:
                    continue

    def get_locations(self):
        for position in number_generator(8):
            try:
                location = self.table[position].find_all('td')
            except IndexError:
                print(f"Internal function 'locations' fails, because position is out of range")
                break

            self.__map_population(location, position)
    
    def obtain_moves(self, information:str=None, scrap:list[NavigableString | Tag]=None, regional:bool=None):
        func = explore_maps(category=information)
        moves_list = getattr(self, information, None)
        content = make_it_table(scrap=scrap, category=information, regional_form=regional, pokemon_name=self.pokemon.p_name, function=func)
        moves_list.append(content)

    def __move_set(self, table:list=None, value:int=None, lenght:int=None, list_name:str=None, atk_type:str=None, form_control:str=None):

        to_populate = getattr(self,list_name)
        to_populate.extend([table[value:value+lenght]])

        for i in to_populate:
            if atk_type == 'Egg Move':
                del i[7]
                i[0] = i[0].text
                i[1] = elements_atk(i[1])
                i[2] = elements_atk(i[2],1)
            
            elif atk_type in ['TM','TR','Technical Machine','Technical Record']:
                i[0] = i[0].text    
                i[1] = i[1].text
                i[2] = elements_atk(i[2])
                i[3] = elements_atk(i[3],1)
            
            else:
                i[1] = i[1].text
                i[2] = elements_atk(i[2])
                i[3] = elements_atk(i[3],1)