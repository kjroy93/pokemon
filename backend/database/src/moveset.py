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
import pandas as pd
import numpy as np

# Libraries made for this proyect
from backend.database.src.parse import number_generator
from backend.database.src.creature import Pokemon

class Moveset():
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon
        self.lv = []
        self.tm_hm = []
        self.tr = []
        self.egg_moves = []
        self.dynamax = []
        self.transfer = []
        self.z_moves = []
    
    def categorization(self):
        knowledge = [
            'Level Up',
            'TM',
            'Technical Machine',
            'HM',
            'Hidden Machine',
            'TR',
            'Technical Record',
            'Egg Moves',
            'Move Tutor',
            'Z Moves',
            'Transfer',
            'Max Moves',  
        ]

        table = self.pokemon.__basic_tables('moveset')

        self.positions = []
        for position in number_generator(8):
            if table[position][0].text in knowledge:
                self.positions.append(position)
            else:
                break
    
    def number_location(self, e, table):
        if isinstance(e, list):
            for i in e:
                    try:
                        location = table[i].text
                        if 'This' in location:
                            p_s = i
                        else:
                            raise ValueError('There is no text description')
                    except ValueError:
                        continue
            
            return p_s
    
    def make_dataframe(self):
        def variable_control(data:list):
            text = data[0].text

            if [
                'Level Up',
                'TM',
                'Technical Machine',
                'HM',
                'TR',
                'Technical Record',
                'Egg Moves'] in text:
                return 9
            elif 'Move Tutor' in text:
                return 8
            elif 'Max Moves' in text:
                return [9,10,11]

        for pos in self.positions:
            info = []
            info.append(pos)
        
            data = info[1:]
            org = [item for sublist in data for item in sublist]
            e = variable_control(data)

            if isinstance(e, list):
                p_s = self.number_location(e,data)
            else:
                pass

            if p_s:
                match p_s:
                    case 9:
                        pass

            reshape = []
            i = 0

            while i < len(org):
                if i == 0:
                    reshape.extend([org[i:i+e]])
                elif 'The' in org[i+8].text:
                    reshape.extend([org[i:i+e]])
                else:
                    sublist = org[i:i+8]
                    sublist.insert(7, 'N/A')
                    reshape.extend([sublist])
                    i -= 1
