# Standard libraries of Python

from functools import wraps
from typing import Literal,Callable

# Dependencies
import requests
import re
from bs4 import BeautifulSoup,ResultSet

from .parse import get_parents,process_ability,process_form_ability,process_hidden_ability,find_table_by_class,elemental_types,stats_calculation

URL = "https://www.serebii.net/index2.shtml"

assert requests.get(URL).status_code == 200, 'There is a problem with Serebii webpage'

def gen_url(gen: int):
    gens = {
        1: 'pokedex',
        2: 'pokedex-gs',
        3: 'pokedex-rs',
        4: 'pokedex-dp',
        5: 'pokedex-bw',
        6: 'pokedex-xy',
        7: 'pokedex-sm',
        8: 'pokedex-swsh'
    }

    return gens[gen]

class Pokemon():
    def __init__(self, gen:int, number_name):
        """
        Clase que representa un Pokémon.

        Parameters:
        - gen (int): Generación del Pokémon.
        - number_name (int/str): Número del Pokémon (para gen < 8) o nombre del Pokémon (para gen >= 8).

        Attributes:
        - html: Contiene el HTML de la página del Pokémon.
        - soup: BeautifulSoup object para analizar la página HTML.
        - number: Número del Pokémon.
        - gen: Generación del Pokémon.
        """

        if gen < 8 and not isinstance(number_name, int):
            raise ValueError("If gen is less than 8, number_name should be an integer.")
        elif gen >= 8 and not isinstance(number_name, str):
            raise ValueError("If gen is 8 or greater, number_name should be a string.")

        chain = gen_url(gen)
        if gen != 8:
            url = f'https://www.serebii.net/{chain}/{str(number_name).zfill(3)}.shtml'
        else:
            url = f'https://www.serebii.net/{chain}/{number_name}/'
        
        self.html = requests.get(url)
        self.soup = BeautifulSoup(self.html.text, 'html.parser')
        self.number = '#{}'.format(str(number_name).zfill(3))
        self.gen = gen

    def __basic_tables(self, type_of_table: str) -> ResultSet:
        all_divs = self.soup.find_all('div', attrs={'align': 'center'})

        match type_of_table:
            case 'fooinfo':
                return find_table_by_class(self.gen,all_divs,'fooinfo',0)
            
            case 'footype':
                return find_table_by_class(self.gen,all_divs,'footype',0)
            
            case 'bases':
                return all_divs
   
    def name(self):
        table = self.__basic_tables('fooinfo')
        location = table[1]
        self._name = location.text
    
    def gender(self):
        self._gender_info = []
        strings_to_search = 'Genderless','Unknown'
        table = self.__basic_tables('fooinfo')
        location = table[4]

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
        table = self.__basic_tables('fooinfo')
        location = table[6]
        height = location.br.next_sibling.text
        self._height = height.split('\r\n\t\t\t').pop(1)

    def weight(self):
        location = self.__basic_tables('fooinfo')[7]
        weight = location.br.next_sibling.text
        self._weight = weight.split('\r\n\t\t\t').pop(1)

    def capture_rate(self):
        location = self.__basic_tables('fooinfo')[8]
        self._capture_rate = int(location.text)
    
    def breeding_steps(self):
        location = self.__basic_tables('fooinfo')[9]
        self._egg_steps = int(location.text.replace(',',''))

    def abilities(self):
        self._abilities = {'ability': [], 'hidden_ability': []}
        self._form_abilities = {'ability': [], 'hidden_ability': []}

        location = self.__basic_tables('fooinfo')[10]
        tags = location.find_all('b')

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

    def __process_formulary(self, location, form_name):
        box = location.find('form', {'name': form_name}).find_all('option')
        parents = [p.text for p in box]
        return get_parents(parents)

    def egg_group(self):
        location = self.__basic_tables('fooinfo')[15]
        quantity = len(location.find_all('form'))

        if quantity > 1:
            self._parents_0 = self.__process_formulary(location,'breed')
            self._parents_1 = self.__process_formulary(location,'breed2')
        else:
            self._parents_0 = self.__process_formulary(location,'breed')
    
    def weakness(self):
        effectiveness = []

        location = self.__basic_tables('footype')

        elements = elemental_types(location)

        filtered = [tag for tag in location if '*' in tag.get_text(strip=True)]
        filtered_t = [i.text for i in filtered]

        val = list(map(lambda x: x.replace('*',''),filtered_t))

        for i in val:
            try:
                effectiveness.append(int(i))
            except ValueError:
                effectiveness.append(float(i))

        self._weakness = dict(zip(elements,effectiveness))
    
    def stats(self):
        location = self.__basic_tables('bases')
        bases = location[0].find('td', string=re.compile("Base Stats - Total.*")).find_next_siblings('td')

        self._hp = int(bases[0].text)
        self._atk = int(bases[1].text)
        self._def = int(bases[2].text)
        self._sp_atk = int(bases[3].text)
        self._sp_def = int(bases[4].text)
        self._spd = int(bases[5].text)

class Mega_Pokemon():
    def __init__(self):
        self.pokemon = Pokemon()