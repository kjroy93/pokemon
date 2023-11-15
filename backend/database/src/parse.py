# Standard libraries of Python
import re

# Dependencies
import pandas as pd
from pandas import DataFrame
from typing import List

elemental_types = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fight', 'Poison', 'Ground', 'Flying', 'Psychc', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

def s_modify(pokemons: str):
    result = re.sub(r'(?<=[a-z])(?=[A-Z])', ',', str(pokemons))
    result = result[2:-2]
    result = result.split(',')
    result = result[1:]

    return result

def identity(df: List[DataFrame]) -> DataFrame:
    name = df[36]
    name.drop(columns=[1],index=[0],inplace=True)

    return name

def gender(df: List[DataFrame]) -> DataFrame:
    gender = df[38]
    gender = gender.set_index(0).T

    return gender

def weight(df: List[DataFrame]):
    height_weight = df[40]
    height_weight.columns = height_weight.iloc[0]
    height_weight = height_weight[1:]
    height_weight = height_weight.apply(lambda col: col.str.split().str[1])

    return height_weight

def hab(df: List[DataFrame]):
    abilities = df[9]
    criteria = '. Hidden Ability (Available through transfer): '
    abilities = abilities.loc[1,1].split(criteria)
    hab_df = pd.DataFrame([
        {'Ability': abilities[0], 'Hidden Ability': abilities[1]}
    ])

    return hab_df

def weaknesses(df: List[DataFrame]):
    weaknesses = df[10]
    weaknesses.drop(index=0, inplace=True)
    weaknesses = weaknesses.reset_index(drop=True)
    weaknesses.iloc[0] = elemental_types
    weaknesses.columns = ['weaknesses'] * len(weaknesses.columns)

    return weaknesses

def egg_group(df: List[DataFrame]):
    egg_group = df[13]
    amount = len(egg_group)

    match amount:
        case 2:

            groups = range(0,2)

            for group in groups:
                group_1 = egg_group.loc[group,0].split()
                group_1 = s_modify(group_1)

                group_2 = egg_group.loc[group,0].split()
                group_2 = s_modify(group_2)
            
            egg_df = pd.DataFrame([
                {'1': group_1,
                 '2': group_2}
            ])
            
            return egg_df
        
        case 1:
            
            group = egg_group.loc[0,0]
            group = s_modify(group)

            egg_df = pd.DataFrame([
                {'1': group}
            ])
        
            return egg_df
        
        case _:

            egg_df = pd.DataFrame([
                {'1': 'This pokémon can not breed'}
            ])

            return egg_df