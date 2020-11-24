# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 22:02:37 2020

@author: JZ2018
"""


import pandas as pd
import numpy as np
import os

box_dir = 'D:/JZR/nba/boxscores'
team_dir = 'D:/JZR/nba/teaminfo'

box_columns = ['Date', 'Name', 'Team', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
                   '3P%','FT', 'FTA', 'FT%', 'ORB', 
                   'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+-','Team_Name','Season']
    

team_columns = ['NUMBER', 'PLAYER', 'POS', 'HEIGHT', 'WEIGHT', 'BIRTH_DATE',
       'NATIONALITY', 'EXPERIENCE', 'COLLEGE', 'team_name', 'team_abrv', 'Season']

month_list = ('September','October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June')

def read_folder(file_dir, df_columns, datatype):

    df = pd.DataFrame(columns = df_columns)
    
    file_list = os.listdir(file_dir)
    
    for f in file_list:
        read_dir = file_dir + '/' + f
        temp_df = pd.read_csv(read_dir)
        temp_df = temp_df.loc[:, ~temp_df.columns.str.contains('^Unnamed')]
        result_df = temp_df.drop_duplicates()
        if datatype == 'box':           
            season = (f.split('Season_'))[1].split('_BoxScores')[0]
            for m in month_list:
                if season.endswith(m):
                    season = season.replace(m, '')
            result_df['Season'] = season
        elif datatype == 'team':
            season = (f.split('Season_'))[1].split('_teamInfo')[0]
            result_df['Season'] = season      
        else:
            result_df['Season'] = ''
        df = df.append(result_df)
            
    return df

box_df = read_folder(box_dir, box_columns, 'box')
team_df = read_folder(team_dir, team_columns, 'team')
box_df.to_csv('D:/JZR/nba/full_boxscores.csv')
team_df.to_csv('D:/JZR/nba/full_teaminfo.csv')

team_df = team_df.rename(columns={'PLAYER':'Name', 'team_name':'Team_Name'})    
#checkt = team_df.query('Name=="Hollis Thompson" & Season=="2015-16"')
combine_df = box_df.merge(team_df, on=['Name', 'Season', 'Team_Name'], how='left')
combine_df.fillna(0)
combine_df.to_csv('D:/JZR/nba/full_combined.csv')
