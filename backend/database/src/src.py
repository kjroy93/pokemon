# Standard libraries of Python

from functools import wraps
from typing import Literal,Callable

# Dependencies
import requests
import re
from bs4 import BeautifulSoup,ResultSet

from .extract import get_parents,process_ability,process_form_ability,process_hidden_ability

URL = "https://www.serebii.net/index2.shtml"

assert requests.get(URL).status_code == 200, 'There is a problem with Serebii webpage'

class Pokemon():
    def __init__(self, pokemon_number: int):
        url = 'https://www.serebii.net/pokedex-sm/{}.shtml'.format(str(pokemon_number).zfill(3))
        self.html = requests.get(url)
        self.soup = BeautifulSoup(self.html.text, 'html.parser')
        self.number = '#{}'.format(str(pokemon_number).zfill(3))

    def __basic_tables(self) -> ResultSet:

        all_divs = self.soup.find_all('div', attrs={'align': 'center'})
        foo_info = all_divs[0].find_all('td', {'class': 'fooinfo'})

        return foo_info

    
    def name(self):
        location = self.__basic_tables('foo_info')[1]
        self._name = location.text
    
    def gender(self):
        self._gender_info = []
        strings_to_search = 'Genderless','Unknown'
        location = self.__basic_tables('foo_info')[4]

        list_to_search = location.text.split()

        if strings_to_search[0] in list_to_search:
            self._gender_info = strings_to_search[0]
        elif strings_to_search[1] in list_to_search:
            self._gender_info = strings_to_search[1]

        genders = location.select('td.fooinfo font')

        for gender in genders:
            sym = gender.text
            percentage = gender.find_next('td').text.strip()
            gender_info_entry = f"{sym}: {percentage}"
            self._gender_info.append(gender_info_entry)

    def height(self):
        location = self.__basic_tables('foo_info')[6]
        height = location.br.next_sibling.text
        self._height = height.split('\r\n\t\t\t').pop(1)

    def weight(self):
        location = self.__basic_tables('foo_info')[7]
        weight = location.br.next_sibling.text
        self._weight = weight.split('\r\n\t\t\t').pop(1)

    def capture_rate(self):
        location = self.__basic_tables('foo_info')[8]
        self._capture_rate = int(location.text)
    
    def breeding_steps(self):
        location = self.__basic_tables('foo_info')[9]
        self._egg_steps = int(location.text.replace(',',''))

    def abilities(self,tags):
        self._abilities = {'ability': [], 'hidden_ability': []}
        self._form_abilities = {'ability': [], 'hidden_ability': []}
        skip_next_flag = False
        form_abilities_flag = False

        for tag in tags:
            if skip_next_flag:
                skip_next_flag = False
                continue

            if "Hidden Ability" in tag.text:
                skip_next_flag = process_hidden_ability(tag, self._abilities, self._form_abilities, skip_next_flag, form_abilities_flag)
            else:
                form_abilities_flag = process_form_ability(tag, form_abilities_flag)
                process_ability(tag, self._abilities, self._form_abilities, form_abilities_flag)

        form_abilities_flag = False

    def __process_form(self, location, form_name):
        box = location.find('form', {'name': form_name}).find_all('option')
        parents = [p.text for p in box]
        return get_parents(parents)

    def egg_group(self):
        location = self.__basic_tables('foo_info')[15]
        quantity = len(location.find_all('form'))

        if quantity > 1:
            self._parents_0 = self.__process_form(location,'breed')
            self._parents_1 = self.__process_form(location,'breed2')
        else:
            self._parents_0 = self.__process_form(location,'breed')