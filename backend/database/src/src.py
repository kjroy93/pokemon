from typing import Tuple

#Dependencies
import requests
import re
from bs4 import BeautifulSoup,ResultSet,Tag

from backend.database.src import parse

URL = "https://www.serebii.net/index2.shtml"

assert requests.get(URL).status_code == 200, 'There is a problem with Serebii webpage'

def gen_url(gen: int):
    """
    It defines an aspect of the URL of the webpage.
    The gen attribute goes from 1 to 8. It is mandatory, in order for the program to work. You use it in the beginning of Pokémon class."
    """
    gens = {
        1: 'pokedex',
        2: 'pokedex-gs',
        3: 'pokedex-rs',
        4: 'pokedex-dp',
        5: 'pokedex-bw',
        6: 'pokedex-xy',
        7: 'pokedex-sm',
        8: 'pokedex-swsh',
        9: 'pokedex-sv'
    }

    return gens[gen]

class Pokemon():
    def __init__(self, gen:int, number_name:Tuple[int|str]):
        """
        Class that represents a Pokémon.

        Parameters:
        - gen (int): The game data you want to see. Please consider, that you must introduce a number, or is not gonna work.
        - number_name (int/str): Pokémon number (for gen < 8) or Pokémon name (for gen >= 8).

        Basic Attributes:
        - html: It contains the HTML of the webpage we are going to scrap This is done with requests library.
        - soup: BeautifulSoup object that contains the HTML text from the webpage.
        - p_number: Pokémon number.
        - gen: Generation.

        Every attribute that contains 'p_', represents the information of the Pókemon you scrapted.

        You can use any of the methods provided in this class. There is no mandatory execution order. For futher information,
        please refer to them.

        """

        if gen < 8 and not isinstance(number_name, int):
            raise ValueError("If gen is less than 8, number_name should be an integer.")
        elif gen >= 8 and not isinstance(number_name, str):
            raise ValueError("If gen is 8 or greater, number_name should be a string.")

        chain = gen_url(gen)
        if gen < 8:
            url = f'https://www.serebii.net/{chain}/{str(number_name).zfill(3)}.shtml'
        elif gen >= 8:
            url = f'https://www.serebii.net/{chain}/{number_name}/'
        
        self.html = requests.get(url)
        self.soup = BeautifulSoup(self.html.text, 'html.parser')
        self.p_number = '#{}'.format(str(number_name).zfill(3))
        self.gen = gen

    def __basic_tables(self, type_of_table: str) -> ResultSet:
        """
        Private method that specifies the classes to searcth in the HTML.text soup:

        Attribute:
        
        - type_of_table: it contains the string that specifies the class to be located.
        
        """
        all_divs = self.soup.find_all('div', attrs={'align': 'center'})

        match type_of_table:
            case 'fooinfo':
                return parse.find_table_by_class(self.gen,all_divs,'fooinfo')
            
            case 'footype':
                return parse.find_table_by_class(self.gen,all_divs,'footype')
            
            case 'bases':
                return all_divs
            
            case 'elements':
                return parse.find_table_by_class(self.gen,all_divs,'cen')

    def __process_formulary(self, location:Tag, form_name:str):
        box = location.find('form', {'name': form_name}).find_all('option')
        parents = [p.text for p in box]
        return parse.get_parents(parents)
   
    def name(self):
        """
        Method to obtain the name of the Pokémon:
        
        Attribute:

        - p_name: Pokémon name
        """
        table = self.__basic_tables('fooinfo')
        location = table[1]
        self.p_name = location.text
    
    def gender(self):
        """
        It defines the % of the Pokémon Gender. This matters specially if you want to breed Pokémon an inherit Hidden Ability more easilly:

        Female has a 60% chance of pass her Hidden Ability. It also, allways pass the Pokeball where she was captured.\n

        Males pass Hidden Ability if the other parent is a Ditto. It also applies to his Pokeball. Males also pass their movements.
        This means, that if the species of the mother learns that move inherited via egg, the father pass that move.\n

        Genderless Pokémon can pass their Hidden Ability and Pokeball with a Ditto parent.

        Please note that if the parents are from the same species, the Pokeball has 50% chance of inherith any of them.\n

        - p_gender_info: gender probability

        """
        self.p_gender_info = []
        strings_to_search = 'Genderless','Unknown'
        table = self.__basic_tables('fooinfo')
        location = table[4]

        list_to_search = location.text.split()

        if strings_to_search[0] in list_to_search:
            self.p_gender_info = strings_to_search[0]
        elif strings_to_search[1] in list_to_search:
            self.p_gender_info = strings_to_search[1]

        genders = location.select('td.fooinfo font')

        for gender in genders:
            sym = gender.text
            percentage = gender.find_next('td').text.strip()
            gender_info_entry = f'{sym}: {percentage}'
            self.p_gender_info.append(gender_info_entry)
    
    def elements(self):
        """

        It determines the elemental types of the Pokémon. This is basic in order to know weakness and STAB (explained later in Damage Calculation).

        - p_elements: Elemental Type of Pokemon.

        """
        table = self.__basic_tables('elements')
        location = table[0]

        self.p_elements = parse.elemental_types(location)

    def height_weight(self):
        """
        It defines the height of the Pokémon. Just fun fact.\n
        It also defines the weight, because some moves use this information to calculate the damage

        Attributes:
        - p_height: height of Pokémon
        - p_weight: weight of Pokémon

        """
        table = self.__basic_tables('fooinfo')
        location_h = table[6]
        location_w = table[7]

        text = location_h.find_all(parse.find_word)

        if text:
            self.p_height = parse.form_standard_case(location_h,'m')
            self.p_weight = parse.form_standard_case(location_w,'kg')
        else:
            self.p_height = parse.find_atribute(location_h)
            self.p_weight = parse.find_atribute(location_w)

    def capture_rate(self):
        table = self.__basic_tables('fooinfo')
        location = table[8]
        self.p_capture_rate = int(location.text)
    
    def breeding_steps(self):
        table = self.__basic_tables('fooinfo')
        location = table[9]
        self.p_egg_steps = int(location.text.replace(',',''))

    def abilities(self):
        self.p_abilities = {'ability': [], 'hidden_ability': []}
        self.p_form_abilities = {'ability': [], 'hidden_ability': []}

        table = self.__basic_tables('fooinfo')
        location = table[10]

        tags = location.find_all('b')

        skip_next_flag = False
        form_abilities_flag = False

        for tag in tags:
            if skip_next_flag:
                skip_next_flag = False
                continue

            if "Hidden Ability" in tag.text:
                skip_next_flag = parse.process_hidden_ability(tag,self.p_abilities,self.p_form_abilities,skip_next_flag,form_abilities_flag)
            else:
                form_abilities_flag = parse.process_form_ability(tag,form_abilities_flag)
                parse.process_ability(tag,self.p_abilities,self.p_form_abilities,form_abilities_flag)

    def egg_group(self):
        table = self.__basic_tables('fooinfo')
        location = table[15]
        quantity = len(location.find_all('form'))

        if quantity > 1:
            self.p_parents_0 = self.__process_formulary(location,'breed')
            self.p_parents_1 = self.__process_formulary(location,'breed2')
        else:
            self.p_parents_0 = self.__process_formulary(location,'breed')
    
    def get_list_of_weakness(self,types_values:list):
        effectiviness = []
        for i in types_values:
            try:
                effectiviness.append(int(i))
            except ValueError:
                effectiviness.append(float(i))
        
        return effectiviness
    
    def weakness(self):
        location = self.__basic_tables('footype')
        elemental_types = parse.list_of_elements(location)

        normal_val, regional_val = parse.get_filters(location)

        normal_weakness = self.get_list_of_weakness(normal_val)
        
        if not regional_val:
            regional_weakness = []
        else:
            regional_weakness = self.get_list_of_weakness(regional_val)

        if not regional_weakness:
            self.p_weakness = dict(zip(elemental_types,normal_weakness))
        else:
            self.p_normal_weakness = dict(zip(elemental_types,normal_weakness))
            self.p_regional_weakness = dict(zip(elemental_types,regional_weakness))
    
    def stats(self):
        location = self.__basic_tables('bases')
        bases = location[0].find('td', string=re.compile("Base Stats - Total.*")).find_next_siblings('td')

        self.p_hp = int(bases[0].text)
        self.p_atk = int(bases[1].text)
        self.p_def = int(bases[2].text)
        self.p_sp_atk = int(bases[3].text)
        self.p_sp_def = int(bases[4].text)
        self.p_spd = int(bases[5].text)

class Mega_Pokemon():
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon
    
    def __basic_tables(self, type_of_table:str, form:str='form') -> ResultSet:
        """
        Private method that specifies the classes to searcth in the HTML.text soup:

        Attribute:
        
        - type_of_table: it contains the string that specifies the class to be located.

        The main difference with Pokemon class, is that the Attribute form comes by default, so it does not need to change.
        
        """
        all_divs = self.pokemon.soup.find_all('div', attrs={'align': 'center'})

        match type_of_table:
            case type_of_table:
                table = parse.find_table_by_class(self.pokemon.gen,all_divs,'fooinfo',form)
                n_f_position = parse.detect_new_forms(self.pokemon.p_name,table)

                if isinstance(n_f_position,str):
                    raise ValueError(n_f_position)
                
                return table, n_f_position
    
    def name(self):
        try:
            table,position = self.__basic_tables('fooinfo')
            location = table[position+1].find('td', class_='fooinfo')
            self.m_name = location.text
        except ValueError as e:
            print(f'Error: {e}')
    
    def elements(self):
        try:
            table,position = self.__basic_tables('fooinfo')
            location = table[position+1].find('td', class_='cen')
            self.m_elements = parse.get_elemental_types(location,None,'yes',self.pokemon.elemental_types)
        except ValueError as e:
            print(f'Error: {e}')
    
    def weakness(self):
        m_weak = []

        if self.m_elements == self.pokemon.p_elements:
            pass

        else:
            try:
                table,position = self.__basic_tables('fooinfo')
                location = table[position+2]
                filtered = list(filter(lambda x: '*' in x.text, location.find_all('td', {'class': 'footype'})))
                filtered = [tag.text for tag in filtered if '*' in tag.get_text(strip=True)]

                val = list(map(lambda x: x.replace('*',''),filtered))

                for i in val:
                    try:
                        m_weak.append(int(i))
                    except ValueError:
                        m_weak.append(float(i))
                
                self.m_weakness = dict(zip(self.pokemon.elemental_types,m_weak))
            except ValueError as e:
                print(f'Error : {e}')
    
    def m_base(self):
        try:
            table,position = self.__basic_tables('base')

            bases = table[position+4].find('td', string=re.compile("Base Stats - Total.*")).find_next_siblings('td')
            
            self.m_hp = int(bases[0].text)
            self.m_atk = int(bases[1].text)
            self.m_def = int(bases[2].text)
            self.m_sp_atk = int(bases[3].text)
            self.m_sp_def = int(bases[4].text)
            self.m_spd = int(bases[5].text)  
        except ValueError as e:
            print(f'Error: {e}')