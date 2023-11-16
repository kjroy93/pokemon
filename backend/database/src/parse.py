# Standard libraries of Python

from functools import wraps
from typing import Literal,Callable

# Dependencies
import requests
import re

from bs4 import BeautifulSoup,ResultSet

URL = "https://www.serebii.net/index2.shtml"

assert requests.get(URL).status_code == 200, 'There is a problem with Serebii webpage'

def with_location_info(division: int, select_table: Literal['foo', 'foo_info']) -> Callable:
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            location = self.__basic_tables(division, select_table)
            return method(self, location, *args, **kwargs)
        return wrapper
    return decorator

class Dextable():
    def __init__(self, pokemon_number: int):
        url = 'https://www.serebii.net/pokedex-sm/{}.shtml'.format(str(pokemon_number)).zfill(3)
        self.html = requests.get(url)
        self.soup = BeautifulSoup(self.html.text, 'html.parser')
        self.number = '#{}'.format(str(pokemon_number).zfill(3))

    def __basic_tables(self, division: int, select_table: Literal['foo','foo_info']) -> ResultSet:

        assert division > 1, 'The number can not be higher than 1'

        all_divs = self.soup.find_all('div', attrs={'align': 'center'})
        foo = all_divs[division].find_all('td', {'class': 'foo'})
        foo_info = all_divs[division].find_all('td', {'class': 'fooinfo'})

        if select_table == 'foo':
            return foo
        elif select_table == 'foo_info':
            return foo_info
    
    @with_location_info(0,'foo_info')
    def get_name(self, location):
        self._name = location[1].text
    
    @with_location_info(4,'foo_info')
    def get_gender(self, location):
        self.gender_info = []
        genders = location.select('td.fooinfo font')

        for gender in genders:
            sym = gender.text
            percentage = gender.find_next('td').text.strip()
            self.gender_info.append(sym,percentage)
    
    @with_location_info(6,'foo_info')
    def get_height(self, location):
        height = location.br.next_sibling.text
        self.height = height.split('\r\n\t\t\t').pop(1)
    
    @with_location_info(7,'foo_info')
    def get_weight(self, location):
        weight = location.br.next_sibling.text
        self.weight = weight.split('\r\n\t\t\t').pop(1)
    
    @with_location_info(9,'foo_info')
    def breeding_steps(self, location):
        self.steps = location.text
    
    @with_location_info(10,'foo_info')
    def get_abilities(self, location):
        tags = location.find_all('b')

        for tag in tags:
            ability = tag.string

            if ability == 'Hidden Ability':
                continue
        
            ability_text = ability.next_element.strip()

            abilities = [ability,ability_text]
            self.abilities = ''.join(abilities)
    
    @with_location_info(15,'foo_info')
    def egg_group(self, location):

        quantity = len(location.find_all('form'))

        if quantity > 1:
            counter = 0
            for formulary in location:
                box = formulary.find('form', {'name': 'breed'}).find_all('option')
                parent = [p.text for p in box]
                counter += 1