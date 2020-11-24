# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 19:32:56 2020

@author: JZ2018
"""


season_end_year = 2019
output_filedir = 'D:/JZR/nba/boxscores/'


import os
#print(os.getcwd())
from bs4 import BeautifulSoup 
import requests
import pandas as pd

team_dictionary = {
    'Atlanta Hawks': 'Atl', 'Boston Celtics': 'Bos', 
    'Brooklyn Nets': 'Brk', 'Charlotte Hornets': 'Cho', 
    'Chicago Bulls': 'Chi', 'Cleveland Cavaliers': 'Cle', 
    'Dallas Mavericks': 'Dal', 'Denver Nuggets': 'Den', 
    'Detroit Pistons': 'Det','Golden State Warriors': 'GSW', 
    'Houston Rockets': 'Hou', 'Indiana Pacers': 'Ind',
    'Los Angeles Lakers': 'LAL', 'Los Angeles Clippers': 'LAC', 
    'Memphis Grizzlies': 'Mem', 'Miami Heat': 'Mia', 
    'Milwaukee Bucks': 'Mil', 'Minnesota Timberwolves': 'Min', 
    'New Orleans Pelicans': 'Nop', 'New York Knicks': 'NYK', 
    'Oklahoma City Thunder': 'OKC', 'Orlando Magic': 'Orl', 
    'Philadelphia 76ers': 'Phi', 'Phoenix Suns': 'Pho', 
    'Portland Trail Blazers': 'Por', 'Sacramento Kings': 'Sac', 
    'San Antonio Spurs': 'SAS', 'Toronto Raptors': 'Tor', 
    'Utah Jazz': 'Uta', 'Washington Wizards': 'Was'
}

def get_roster(team, season_end_year):
    r = requests.get(f'https://www.basketball-reference.com/teams/{team}/{season_end_year}.html')
    df = None
    if r.status_code==200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        df = pd.read_html(str(table))[0]
        df.columns = ['NUMBER', 'PLAYER', 'POS', 'HEIGHT', 'WEIGHT', 'BIRTH_DATE',
                        'NATIONALITY', 'EXPERIENCE', 'COLLEGE']
        #df['PLAYER'] = df['PLAYER'].apply(lambda name: remove_accents(name, team, season_end_year))
        df['BIRTH_DATE'] = df['BIRTH_DATE'].apply(lambda x: pd.to_datetime(x))
        df['NATIONALITY'] = df['NATIONALITY'].apply(lambda x: x.upper())
    return df

def get_team_stats(team_dictionary, season_end_year):
    df_columns = ['NUMBER', 'PLAYER', 'POS', 'HEIGHT', 'WEIGHT', 'BIRTH_DATE',
       'NATIONALITY', 'EXPERIENCE', 'COLLEGE', 'team_name', 'team_abrv']
    team_df = pd.DataFrame(columns = df_columns)
    
    for t in team_dictionary:
        team = str(team_dictionary[t]).upper()
        roster_df = get_roster(team, season_end_year)
        roster_df['team_name'] = str(t)
        roster_df['team_abrv'] = team_dictionary[t]
        team_df = team_df.append(roster_df)
        
    return team_df


team_data = get_team_stats(team_dictionary, season_end_year)

outfile = output_filedir + 'Season_' + str(season_end_year-1) + '-' + str(season_end_year) + '_teamInfo'
team_data.to_csv(f'{outfile}.csv')
