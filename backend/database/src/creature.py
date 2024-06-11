# Standard libraries of Python
from typing import Tuple, Literal

# Dependencies
import requests
import re
from bs4 import BeautifulSoup, ResultSet, Tag

# Libraries made for this proyect
from backend.database.src import parse
from backend.database.utils import functions
from backend.database.special_cases import rotom, heroes, urshifu, darmanitan, tauros, necrozma, hoopa, calyrex, ogerpon

URL = "https://www.serebii.net/index2.shtml"

assert requests.get(URL).status_code == 200, 'There is a problem with Serebii webpage'

def gen_url(gen: int):
    """
    It defines an aspect of the URL of the webpage.
    The gen attribute goes from 1 to 9. It is mandatory, in order for the program to work. You use it in the beginning of Pokémon class."
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
        if self.html.status_code == 200:
            self.soup = BeautifulSoup(self.html.text, 'html.parser')
        else:
            raise ValueError('This Pokemon does not exist in web page')
        
        self.p_number = '#{}'.format(str(number_name).zfill(3))
        self.gen = gen
        location = self._basic_tables('footype')
        self.elemental_types = functions.list_of_elements(location)
        self._bases = []

    def _basic_tables(self, type_of_table:Literal['fooinfo','footype','bases','elements','moveset']) -> ResultSet:
        """
        Method that specifies the classes to searcth in the HTML.text soup.\n
        ¡WARNING! In case of 'elements', 'bases' and 'moveset', please, specify it in the parameter.

        Parameter:
        
        - type_of_table: it contains the string that specifies the class or table to be located.
        
        """
        all_divs = self.soup.find_all('div', attrs={'align': 'center'})

        match type_of_table:
            case 'fooinfo':
                return parse.find_table_by_class(self.gen,all_divs,class_name=type_of_table)
            
            case 'footype':
                return parse.find_table_by_class(self.gen,all_divs,class_name=type_of_table)
            
            case 'bases':
                return all_divs
            
            case 'elements':
                return parse.find_table_by_class(self.gen,all_divs,class_name='cen')
            
            case 'moveset':
                return parse.find_table_by_class(self.gen,all_divs,search=type_of_table)
   
    def name(self):
        """
        Method to obtain the name of the Pokémon:
        
        Attribute:

        - p_name: Pokémon name
        """
        table = self._basic_tables('fooinfo')
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
        table = self._basic_tables('fooinfo')
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

    def _get_elemental_types(self, texts:list, html:Tag, name:str=None) -> dict[str,list]:
        dictionary = {form: [] for form in texts}

        for element in texts:
            location = html.find(string=element).next
            types = parse.elemental_types(location,pokemon=name)
            dictionary[element] = types
        
        return dictionary
    
    def elements(self):
        """

        It determines the elemental types of the Pokémon. This is basic in order to know weakness and STAB (explained later in Damage Calculation).
        
        Attributes:
        - p_elements: Elemental Types of Pokemon.
        - rotoms_elements: Contain the elemental types of all forms of Rotom
        - heroes: Contain the elemental types of Zacian & Zamazenta
        - urshifu_styles: Contain the elemental types of Urshifu

        """
        table = self._basic_tables('elements')
        location = table[0]

        if self.p_name == 'Rotom':
            self.rotom_types = rotom.rotom_types(location)
        
        elif self.p_name in ['Zacian','Zamazenta']:
            self.heroes = heroes.heroes_types(location, self.p_name)
        
        elif 'Urshifu' in self.p_name:
            self.urshifu_styles = urshifu.urshifu_styles(location)
        
        elif 'Darmanitan' in self.p_name:
            self.darmanitan_types = darmanitan.darmanitan_types(location,self.gen)
        
        elif 'Tauros' in self.p_name and self.gen >= 9:
            self.tauros_types = tauros.tauros_types(location)
        
        elif 'Hoopa' in self.p_name:
            self.hoopa_types = hoopa.hoopa_types(location)
        
        elif 'Necrozma' in self.p_name:
            self.necrozma_types = necrozma.necrozma_types(location)
        
        elif 'Calyrex' in self.p_name:
            self.calyrex_types = calyrex.calyrex_types(location)
        
        elif 'Ogerpon' in self.p_name:
            self.ogerpon_types = ogerpon.ogerpon_types(location)

        else:
            self.p_elements = parse.elemental_types(location)

    def height_weight(self):
        """
        It defines the height of the Pokémon. Just fun fact.\n
        It also defines the weight, because some moves use this information to calculate the damage

        Attributes:
        - p_height: height of Pokémon
        - p_weight: weight of Pokémon

        """
        table = self._basic_tables('fooinfo')
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
        table = self._basic_tables('fooinfo')
        location = table[8]
        self.p_capture_rate = int(location.text)
    
    def breeding_steps(self):
        table = self._basic_tables('fooinfo')
        location = table[9]
        self.p_egg_steps = int(location.text.replace(',',''))

    def abilities(self):
        self.p_abilities = {'ability': [], 'hidden_ability': []}
        self.p_form_abilities = {'ability': [], 'hidden_ability': []}

        if self.p_name == 'Lycanroc':
            self.p_third_form = {'ability': []}

        table = self._basic_tables('fooinfo')
        location = table[10]

        tags = location.find_all('b')

        skip_next_flag = False
        form_abilities_flag = False

        if self.p_name == 'Ogerpon':
            self.ogerpon_abilities = ogerpon.ogerpon_abilities(tags)

        counter = 0
        for tag in tags:
            if skip_next_flag:
                skip_next_flag = False
                continue

            if "Hidden Ability" in tag.text:
                skip_next_flag = parse.process_hidden_ability(tag,self.p_abilities,self.p_form_abilities,skip_next_flag,form_abilities_flag)
            elif counter >= 7:
                form_abilities_flag = parse.process_form_ability(tag,form_abilities_flag)
                parse.process_ability(tag,self.p_abilities,self.p_third_form,form_abilities_flag)
            else:
                form_abilities_flag = parse.process_form_ability(tag,form_abilities_flag)
                parse.process_ability(tag,self.p_abilities,self.p_form_abilities,form_abilities_flag)
                   
            counter += 1

    def __process_formulary(self, location:Tag, form_name:str):
        box = location.find('form', {'name': form_name}).find_all('option')
        parents = [p.text for p in box]
        return parse.get_parents(parents)

    def egg_group(self):
        table = self._basic_tables('fooinfo')
        location = table[15]
        quantity = len(location.find_all('form'))

        if quantity > 1:
            self.p_parents_0 = self.__process_formulary(location,'breed')
            self.p_parents_1 = self.__process_formulary(location,'breed2')
        else:
            self.p_parents_0 = self.__process_formulary(location,'breed')
    
    def _get_list_of_weakness(self, pokemon:str, values:list, elemental_types:list, tag:Tag):
        if isinstance(pokemon,str):
            types_values = parse.filter_types(tag)
        else:
            types_values = values

        effectiviness = []
        for i in types_values:
            try:
                effectiviness.append(int(i))
            except ValueError:
                effectiviness.append(float(i))
        
        if pokemon:
            dictionary = functions.make_dict(elemental_types,effectiviness)

            return dictionary
        
        else:
            return effectiviness
    
    def weakness(self):
        location = self._basic_tables('footype')

        if self.p_name in ['Rotom','Zacian','Zamazenta','Urshifu','Darmanitan','Tauros','Hoopa','Calyrex','Necrozma','Ogerpon']:
            self.p_elements = 'init'
        
        if 'Rotom' in self.p_name:
            self.rotom_weakness,self.hr_weakness,self.wr_weakness,self.fr_weakness,self.fanr_weakness,self.mr_weakness = rotom.rotom_weakness(location,self.elemental_types)

        elif self.p_name in ['Zacian','Zamazenta']:
            self.heroe_weakness,self.crowned_weakness = heroes.heroes_weakness(location,self.elemental_types)

        elif 'Urshifu' in self.p_name:
            self.single_weakness,self.rapid_weakness = urshifu.urshifu_weakness(location,self.elemental_types)

        elif 'Darmanitan' in self.p_name:
            match self.gen:
                case 5 | 6 | 7:
                    self.darmanitan_weakness,self.zen_mode_weakness = darmanitan.darmanitan_weakness(location,self.gen,self.elemental_types)
                case 8 | 9:
                    self.darmanitan_weakness,self.galar_darmanitan_weakness,self.zen_mode_weakness,self.galar_zen_weakness = darmanitan.darmanitan_weakness(location,self.gen,self.elemental_types)

        elif 'Tauros' in self.p_name:
            self.tauros_weakness,self.paldean_tauros_weakness,self.blaze_tauros_weakness,self.aqua_tauros_weakness = tauros.tauros_weakness(location,self.elemental_types)
        
        elif 'Hoopa' in self.p_name:
            self.hoopa_c_weakness,self.hoopa_u_weakness = hoopa.hoopa_weakness(location,self.elemental_types)
        
        elif 'Necrozma' in self.p_name:
            self.necrozma_n_weakness,self.necrozma_dusk_weakness,self.necrozma_dawn_weakness = necrozma.necrozma_weakness(location,self.elemental_types)
        
        elif 'Calyrex' in self.p_name:
            self.calyrex_weakness,self.calyrex_i_weakness,self.calyrex_s_weakness = calyrex.calyrex_weakness(location,self.elemental_types)
        
        elif 'Ogerpon' in self.p_name:
            self.ogerpon_t_m_w,self.ogerpon_h_m_w,self.ogerpon_w_m_w,self.ogerpon_c_m_w = ogerpon.ogerpon_weakness(location,self.elemental_types) 
        
        elif 'regional' in self.p_elements:
            regional_weakness = None

            normal_val, regional_val = parse.get_filters(location,1)
            normal_weakness = self._get_list_of_weakness(normal_val)
            regional_weakness = self._get_list_of_weakness(regional_val)

            self.p_normal_weakness = dict(zip(self.elemental_types,normal_weakness))
            self.p_regional_weakness = dict(zip(self.elemental_types,regional_weakness))

        else:
            val = parse.get_filters(location,0)
            weakness = self._get_list_of_weakness(None,val,None,None)
            self.p_weakness = dict(zip(self.elemental_types,weakness))

    def _process_bases(self, location):
        p_hp = int(location[0].text)
        p_atk = int(location[1].text)
        p_def = int(location[2].text)
        p_sp_atk = int(location[3].text)
        p_sp_def = int(location[4].text)
        p_spd = int(location[5].text)

        return p_hp,p_atk,p_def,p_sp_atk,p_sp_def,p_spd

    @property
    def bases(self):
        return self._bases
    
    @bases.setter
    def bases(self, location):
        bases_values = self._process_bases(location)
        self._bases.extend(bases_values)
    
    def stats(self):
        if self.gen < 8:
            location = self._basic_tables('bases')
            bases = location[0].find('td', string=re.compile("Base Stats - Total.*"))

            if len(bases) > 1:
                for base in bases:
                    i = base.find_next_siblings('td')
                    self.bases = i
            else:
                bases = bases.find_next_siblings('td')
                self.bases = bases

        elif self.gen >= 8:
            location = self._basic_tables('bases')
            bases = location[1].find_all('td', string=re.compile("Base Stats - Total.*"))

            if len(bases) > 1:
                for base in bases:
                    i = base.find_next_siblings('td')
                    self.bases = i
            else:
                bases = location[1].find('td', string=re.compile("Base Stats - Total.*")).find_next_siblings('td')
                self.bases = bases
        
        text_form = location[1].find_all('td', {'class': 'fooevo', 'colspan': '8'})

        s = 'Stats - '
        aspect = []
        for i in text_form:
            info = i.text.replace(s,'')
            if info == 'Mega Evolution':
                continue
            aspect.append(info)
        
        self._bases = parse.process_multiple_bases(aspect,self._bases)

class Mega_Pokemon():
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon
        self._bases = []

        all_divs = self.pokemon.soup.find_all('div', attrs={'align': 'center'})
        self._tables = parse.find_table_by_class(self.pokemon.gen,all_divs,search='form')
        self._position,result_message = parse.detect_new_forms(self.pokemon.p_name,self._tables)
        
        if not self._position:
            raise ValueError(result_message)
        elif isinstance(self._position,list) and len(self._position) == 4:
            self._position = self._position[0:2]
        else:
            self._position = self._position[0]

    def __control(self):
        if isinstance(self._position,int):
            return 1
        elif isinstance(self._position,list):
            return len(self._position)
        else:
            raise ValueError("The data must be an integer or a list. Check the input.")
        
    def name(self):
        condition = len(self._position)
        match condition:
            case 2:
                try:
                    names = []
                    for i in self._position:
                        location = self._tables[i+1].find('td', class_='fooinfo')
                        names.append(location.text)
                    self.m_name_0, self.m_name_1 = [name for name in names]
                except ValueError as e:
                    print(f'Error: {e}')
            case 1:
                try:
                    location = self._tables[self._position+1].find('td', class_='fooinfo')
                    self.m_name = location.text
                except ValueError as e:
                    print(f"Error: {e}")

    def __process_element_location(self, position:int, element:Literal['element','ability','weakness']):
        match element:
            case 'element':
                try:
                    location = self._tables[position+1].find('td', class_='cen')
                    
                    return parse.elemental_types(location,'mega',self.pokemon.elemental_types)
                
                except ValueError as e:
                    print(f'Error: {e}')

                    return None
            
            case 'ability':
                try:
                    location = self._tables[position+2].find_all('b')
                    m_ability = {'ability': []}
                    parse.process_ability(location[2],m_ability,None,None)
                    
                    return m_ability
                
                except ValueError as e:
                    print(f'Error: {e}')

                    return None
            
            case 'weakness':
                m_weak = []
                try:
                    location = self._tables[position+3]
                    filtered = list(filter(lambda x: '*' in x.text, location.find_all('td', {'class': 'footype'})))
                    filtered = [tag.text for tag in filtered if '*' in tag.get_text(strip=True)]

                    val = list(map(lambda x: x.replace('*',''),filtered))

                    for i in val:
                        try:
                            m_weak.append(int(i))
                        except ValueError:
                            m_weak.append(float(i))
                    
                    m_weakness = dict(zip(self.pokemon.elemental_types,m_weak))

                    return m_weakness
                
                except ValueError as e:
                    print(f'Error: {e}')

                    return None
    
    def elements(self):
        condition = self.__control()

        match condition:
            case 2:
                self.m_elements_0 = self.__process_element_location(self._position[0],'element')
                self.m_elements_1 = self.__process_element_location(self._position[1],'element')
            case 1:
                self.m_elements = self.__process_element_location(self._position,'element')
    
    def ability(self):
        condition = self.__control()

        match condition:
            case 2:
                self.m_ability_0 = self.__process_element_location(self._position[0],'ability')
                self.m_ability_1 = self.__process_element_location(self._position[1],'ability')
            case 1:
                self.m_ability = self.__process_element_location(self._position,'ability')
    
    def weakness(self):
        condition = self.__control()

        match condition:
            case 2:
                if self.m_elements_0 != self.pokemon.p_elements:
                    self.m_weakness_0 = self.__process_element_location(self._position[0],'weakness')
                else:
                    self.m_elements_0 = self.pokemon.p_weakness

                if self.m_elements_1 != self.pokemon.p_elements:
                    self.m_weakness_1 = self.__process_element_location(self._position[1],'weakness')
                else:
                    self.m_weakness_1 = self.pokemon.p_weakness
            case 1:
                if self.m_elements != self.pokemon.p_elements:
                    self.m_weakness = self.__process_element_location(self._position,'weakness')
                else:
                    self.m_weakness = self.pokemon.p_weakness
    
    @property
    def bases(self):
        return self._bases
    
    @bases.setter
    def bases(self,location):
        bases_values = self.pokemon._process_bases(location)
        self._bases.extend(bases_values)
    
    def m_base(self):
        condition = self.__control()

        match condition:
            case 2:
                try:
                    bases_0 = self._tables[self._position[0]+4].find('td', string=re.compile('Base Stats - Total.*')).find_next_siblings('td')
                    bases_1 = self._tables[self._position[1]+4].find('td', string=re.compile('Base Stats - Total.*')).find_next_siblings('td')

                    self.bases = bases_0
                    self.bases = bases_1

                except ValueError as e:
                    print(f'Error: {e}')
                
                self._bases = parse.process_multiple_bases([self.m_name_0,self.m_name_1],self._bases)

            case 1:
                try:
                    bases = self._tables[self._position+4].find('td', string=re.compile('Base Stats - Total.*')).find_next_siblings('td')

                    self.bases = bases

                except ValueError as e:
                    print(f'Error: {e}')