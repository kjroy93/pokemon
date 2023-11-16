# Standard libraries of Python

from typing import List
from time import gmtime

# Dependencies
import pandas as pd
import requests
import re

from pandas import DataFrame
from bs4 import BeautifulSoup

assert requests.get("https://www.serebii.net/index2.shtml").status_code == 200, 'There is a problem with Serebii webpage'

def str_cleaning(func):
    def wrapper(self):
        table = self.soup.find_all('table', class_='dextable')
        strings = table[1].find_all('table')[2].text.split()
        part_1, part_2 = func(self, strings)

        return part_1, part_2

    return wrapper

def basic_table(func):
    def wrapper(self):
        self.table = self.soup.find_all('table', class_='dextable')
        return func(self)

    return wrapper

class Dextable():
    def __init__(self,pokemon_number: int):
        if pokemon_number < 100:
            self.html_text = requests.get(f'https://www.serebii.net/pokedex-sm/00{pokemon_number}.shtml').text
        else:
            self.html_text = requests.get(f'https://www.serebii.net/pokedex-sm/{pokemon_number}.shtml').text
        
        self.soup = BeautifulSoup(self.html_text, 'html.parser')
    
    def name_cleaning(self, string_with_name: List[str]) -> List[str]:
        text_to_eliminate = '-','','Serebii.net','Pokédex'
        cleaned_name = [element for element in string_with_name if element not in text_to_eliminate]

        return cleaned_name

    def get_name_nro(self):
        self._name = self.soup.find('title').text.split()
        cleaned_name = self.name_cleaning(self._name)
        self._name, self._number = cleaned_name[0], cleaned_name[1]
        self._number = int(re.sub(r'#', '', self._number))
    
    @str_cleaning
    def get_gender(self, strings):
        male_sim, remaining = strings[1].split(':')
        female_sim, f_percent = strings[2].split(':')
        m_percent, female = remaining.split('%')
        f_percent = f_percent.split('%')

        self.male = strings[0]
        self.male_sim = male_sim.strip()
        self.m_percent = m_percent.strip()
        self.female = female.split()
        self.female_sim = female_sim.split()
    
    @basic_table
    def get_type(self):
        types = []
        for element in self.table[1].find_all('td', class_ = 'cen'):
            text_value = element
            for i in text_value:
                types.append(i)
        
        if len(types) == 2:
            multi_list = [types[0].img['alt'].split('-type'),types[2].img['alt'].split('-type')]
            self.elemental_type = [item for sublist in multi_list for item in sublist]
        else:
            self.elemental_type = types.pop(0)