"""File to scrap the data for the move set, including:
- Level up
- TM & HM
- Move Tutors
- Egg Moves
- Z Moves
- Max Moves
- Transfer Moves"""

# Standard Libraries of Python
from typing import Tuple, Literal, Generator

# Dependencies
from bs4 import Tag
import pandas as pd
import numpy as np

# Libraries made for this proyect
from backend.database.utils.functions import number_generator, elements_atk
from backend.database.parsers import parse_movements
from backend.database.src.creature import Pokemon

class Moveset():
    def __init__(self, pokemon: Pokemon):
        self._map = {
            "Level Up": ["lv"], "Form Level Up": ["lv_form"],"TM": ["tm_hm"], 
            "Technical Machine": ["tm_hm"],"HM": ["tm_hm"], "Hidden Machine": ["tm_hm"],
            "TR": ["tr"], "Technical Record": ["tr"], "Egg Moves": ["egg_moves"], "Move Tutor": ["mt"],
            "BDSP":["bdsp_tutor"], "Z Moves": ["z_moves"], "Transfer": ["transfer"], "Max Moves": ["dynamax"]
        }

        self.pokemon = pokemon
        self.table = self.pokemon._basic_tables('moveset')

        self.lv = []
        self.lv_form = []
        self.tm_hm = []
        self.tr = []
        self.egg_moves = []
        self.dynamax = []
        self.transfer = []
        self.z_moves = []
        self.mt = []

        if self.pokemon.gen == 8:
            self.bdsp_tutor = []

        self.positions = []

    def locations(self):
        for position in number_generator(8):
            try:
                location = self.table[position].find_all('td')
            except IndexError:
                print(f"Internal function 'locations' fails, because position is out of range")
                break

            for keyword, p_list in self._map.items():
                if keyword in location[0].text:
                    p_list.append(position)
                    break

    def __missing_data_fix(self, table:list, counter:int=None, atk_type:str=None, form_control:str=None):
        def table_catt(table:list, atk_type:str=None ,category:str=None):
            if category not in [
                'Special',
                'Physical',
                'Other'
            ] and ['Max','Z'] in atk_type:
                table.insert(3, 'N/A')

            elif category not in ['Gigantamax'] and 'Max Moves' in atk_type:
                table.insert(10, 'N/A')
        
        def form_max_z_move(table:list[Tag], category:int, counter:int):
            l = parse_movements.list_lenght(counter,table,category)()
            indexes = parse_movements.execution_pass(table)

            if type(indexes) == list:
                to_fix = parse_movements.max_z_table_segment(counter,l,table,indexes)()
                return to_fix
            else:
                return table[counter:counter+l]
        
        def form_tm():
            pass

        def form_egg():
            pass

        def form_tutor():
            pass
        
        f_x_map = {
            'Max': table_catt,
            'Z': table_catt
        }

        f_y_map = {
            'TM': form_tm,
            'Technical Machine': form_tm,
            'TR': form_tm,
            'Technical Record': form_tm,
            'Egg Move': form_egg,
            'Move Tutor': form_tutor,
            'Max Move': form_max_z_move,
            'Z Move': form_max_z_move
        }

        if isinstance(table, list) and not form_control:
            for key, function in f_x_map.items():
                function(table,atk_type,category=table[counter+3].text)
                if key == 'Max':
                    function(table,atk_type,category=table[counter+10].text)
        
        elif isinstance(table, list) and form_control:
            pass

        else:
            raise ValueError("Table is not a list. Please, check input.")
    
    def __move_set(self, table:list=None, value:int=None, lenght:int=None, list_name:str=None, atk_type:str=None, form_control:str=None):
        self.__missing_data_fix()

        to_populate = getattr(self,list_name)
        to_populate.extend([table[value:value+lenght]])

        for i in to_populate:
            if atk_type == "Egg Move":
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

    def __max_z_move(self, table_type:str=None, table:list=None, value:int=None, lenght:int=None, list_name:str=None, form_control:str=None):
        self.__missing_data_fix(table,counter=value,atk_type=table_type, form_control=form_control)

        to_populate = getattr(self,list_name)
        to_populate.extend([table[value:value+lenght]])
    
    def __list_composition(self, table:list):
        info = []
        for pos in table:
            info.append(pos)
        
        return info
    
    def make_dataframe(self, table_type:str, position:int):
        def table_lenght(control:str, form_control:str=None):
            knowledge = {
                "Level Up": [9, self.__move_set],"Technical Machine": [9, self.__move_set],"TM": [9, self.__move_set],"Technical Record": [9, self.__move_set],
                "TR": [9, self.__move_set],"HM": [9, self.__move_set],"Hidden Machine": [9, self.__move_set],"Egg Move": [9, self.__move_set],
                "Move Tutor": [8, self.__move_set], "Max Move": [11, self.__max_z_move], "Z Move": [11, self.__max_z_move]
            }

            form_knowledge = {
                "Level Up": [9, self.__move_set], "Form Level Up": [9, self.__move_set], "Technical Machine": [12, self.__move_set],"TM": [12, self.__move_set],
                "Technical Record": [12, self.__move_set], "TR": [12, self.__move_set], "HM": [12, self.__move_set], "Hidden Machine": [12, self.__move_set],
                "Egg Move": [8, self.__move_set], "Move Tutor": [10, self.__move_set], "Form Transfer": [9, self.__move_set], "Max Move": [16, self.__max_z_move],
                "Z Move": [16, self.__max_z_move]
            }

            if not (isinstance(control,str) and (form_control is None or isinstance(form_control,str))):
                raise ValueError(f"Error in the type of data in parameter. They must be strings")

            knowledge_dict = knowledge if not form_control else form_knowledge

            for key, value in knowledge_dict.items():
                if key in control:
                    return value

        info = self.__list_composition(self.table[position].find_all('td'))
        form_knowledge = ['Alolan','Galarian','Hisuian','Paldean']
        form_info = self.pokemon.p_elements

        for key in form_info.keys():
            if key in form_knowledge:
                form_control = key
            break