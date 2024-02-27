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
from bs4 import BeautifulSoup, ResultSet
import pandas as pd
import numpy as np

# Libraries made for this proyect
from backend.database.src.parse import number_generator, elements_atk
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
    
    def __move_set(self, org:list=None, value:int=None, lenght:int=None, list_name:str=None, atk_type:str=None, form_control:str=None):
        self.__missing_data_fix()

        to_populate = getattr(self,list_name)
        to_populate.extend([org[value:value+lenght]])

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
        
        def form_table_catt(table:list, atk_type:str=None):
            to_fill = []
            match atk_type:
                case 'TM'|'TR'|'Technical Machine'|'Technical Record':
                    table = list(filter(lambda x: 'table' not in str(x[1]), enumerate(table)))
                    table = list(map(lambda x: x[1], table))

                    i = 0
                    while i < len(table):
                        if hasattr(table[i+9],'get'):
                            l = 11 if i == 0 or isinstance(table[i+9].get('alt',''),str) else 10
                        else:
                            l = 10

                        if l == 10 and any(word in table[i+8].get('alt','') for word in ['Alolan', 'Galarian', 'Hisuian', 'Paldean', 'Normal']):
                            fix = table[i:i+l]
                            fix.insert(8 if 'Form' in table[i+8].get('alt','') else 9, 'N/A')
                            to_fill.extend([fix])
                        else:
                            to_fill.extend([table[i:i+l]])
                        i += l
                    
                    return to_fill
                
                case 'Egg Move':
                    reference = []
                    i = 7
                    while i < len(table):
                        html = str(table[i])
                        soup = BeautifulSoup(html, 'html.parser')

                        img_tag = soup.find_all('img')
                        if img_tag:
                            values = [img.get('alt') for img in img_tag]
                            del table[i]

                            for pos,value in enumerate(values):
                                if pos < 1:
                                    table.insert(i,value)
                                else:
                                    table.insert(i+1,value)

                            i += 10

                        elif table[i].text == 'Details':
                            del table[i]

                            if not reference:
                                reference.append(i-7)
                            
                            i += 8

                        elif table[i+1].text == '':
                            if self.pokemon.p_name == 'Raichu' and table[i].text == 'Volt Tackle':
                                del table[i+7]

                                exclusive_move_case = table[i:]
                                reference.append(i)

                                i += 9

                                continue
                            
                            if len(reference) == 1:
                                reference.append(i)

                            del table[i+1]
                            del table[i+8]

                            i += 9
                        
                        else:
                            i -= 7
                    
                    form_egg_moves = table[0:reference[0]]
                    eightgen_egg_moves = table[reference[0]:reference[1]]
                    bdsp_egg_moves = table[reference[1]:reference[2]]
                    exclusive_move_case = [exclusive_move_case]

                    if exclusive_move_case:
                        return form_egg_moves,eightgen_egg_moves,bdsp_egg_moves,exclusive_move_case
                    else:
                        return form_egg_moves,eightgen_egg_moves,bdsp_egg_moves
        
        f_x_map = {
            'Max': table_catt,
            'Z': table_catt
        }

        f_y_map = {
            'TM': form_table_catt,
            'Technical Machine': form_table_catt,
            'TR': form_table_catt,
            'Technical Record': form_table_catt,
            'Egg Move': form_table_catt,
            'Move Tutor': form_table_catt,
            'Max Move': form_table_catt,
            'Z Move': form_table_catt
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

    def __max_z_move(self, table_type:str=None, org:list=None, value:int=None, lenght:int=None, list_name:str=None, form_control:str=None):
        self.__missing_data_fix(org,counter=value,atk_type=table_type)

        to_populate = getattr(self,list_name)
        to_populate.extend([org[value:value+lenght]])
    
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

        data = info[1:]
        org = [item for sublist in data for item in sublist]
        e = table_lenght(table_type,form_control)

        list_of_list = 0
        for i in range(0,len(org),e):
            for _, str_int in self._map.items():
                atk_str = (str_int[0])
                if 'Max' in table_type or 'Z' in table_type:
                    self.__max_z_move(table_type,org,value=i,lenght=e,list_name=atk_str)
                    break
                else:
                    self.__move_set(org,value=i,lenght=e,list_name=atk_str,atk_type=table_type)
                    break

            list_of_list += 1
        
        to_treat = getattr(self,)