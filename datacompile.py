# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 22:02:37 2020

@author: JZ2018
"""


import pandas as pd
import numpy as np
import os
import re

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
#box_df.to_csv('D:/JZR/nba/full_boxscores.csv')
#team_df.to_csv('D:/JZR/nba/full_teaminfo.csv')

team_df = team_df.rename(columns={'PLAYER':'Name', 'team_name':'Team_Name'})    
#checkt = team_df.query('Name=="Hollis Thompson" & Season=="2015-16"')
combine_df = box_df.merge(team_df, on=['Name', 'Season', 'Team_Name'], how='left')
combine_df = combine_df.fillna(0)
combine_df = combine_df.sort_values(['Name', 'Season', 'Date'])
#combine_df.to_csv('D:/JZR/nba/full_combined.csv')
#combine_df = pd.read_csv('D:/JZR/nba/full_combined.csv')
##--------------------------------------------------------------------------------
min_dates = combine_df.groupby(['Name', 'Season']).agg({'Date':'min'})
min_dates = min_dates.rename(columns={'Date':'Season_start_date'})

combine_df = combine_df.merge(min_dates, on=['Name', 'Season'], how='left')

with pd.option_context('display.max_columns', 40):
    print(combine_df.describe(include='all'))
    print(combine_df.head())
combine_df.dtypes
#combine_df['BIRTH_DATE_str'] = combine_df['BIRTH_DATE'].map(str)
#combine_df['BIRTH_DATE_str'] = combine_df['BIRTH_DATE_str'].str.replace('-','')
#combine_df['Days_since_Bday'] = pd.to_timedelta(combine_df['Days_since_Bday'], 'd')
combine_df['BIRTH_DATE'] = pd.to_datetime(combine_df['BIRTH_DATE'])
combine_df['GameDate'] = pd.to_datetime(combine_df['Date'].astype(str), format='%Y%m%d')
combine_df['Season_start_date'] = pd.to_datetime(combine_df['Season_start_date'].astype(str), format='%Y%m%d')

combine_df['Age'] = (combine_df['GameDate'] - combine_df['BIRTH_DATE']).dt.days
combine_df['Age'] = combine_df['Age']/365
combine_df['Days_in_Season'] = (combine_df['GameDate'] - combine_df['Season_start_date']).dt.days
combine_df['Weeks_in_Season'] = (combine_df['Days_in_Season'] / 7).astype(int)
combine_df['Months_in_Season'] = (combine_df['Days_in_Season'] / 30).astype(int)

agg_columns = ['MP', 'FG', 'FGA', '3P', '3PA',
                   'FT', 'FTA', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

for col in agg_columns:
    agg_name = 'Cum_' + col
    combine_df[agg_name] = combine_df.groupby(['Name', 'Season'])[col].cumsum()


def get_height(h):
    if h == 0:
        output = 0
    else:
        str_h = str(h)
        hs = str_h.split('-')
        h_ft = hs[0]
        h_in = hs[1]
        output = int(h_ft)*12 + int(h_in)
    return output

#get_height('7-0')
    
combine_df['Height_inches'] = combine_df['HEIGHT'].map(lambda x: get_height(x))
combine_df['POS'].value_counts()
ohe_POS = pd.get_dummies(combine_df['POS'], prefix = 'POS')

combine_df = pd.concat([combine_df, ohe_POS], axis = 1)
combine_df['EXPERIENCE_Yrs'] = np.where(combine_df['EXPERIENCE']=='R', 0, combine_df['EXPERIENCE']).astype(int)

combine_df['Month'] = pd.DatetimeIndex(combine_df['GameDate']).month
month_before_Allstar = [10,11,12,1]
combine_df['Before_AllStarWeek'] = np.where(combine_df['Month'].isin(month_before_Allstar), 1, 0)
month_playoff = [4, 5, 6, 7, 8, 9]
combine_df['Playoff'] = np.where(combine_df['Month'].isin(month_playoff), 1, 0)

combine_df.to_csv('D:/JZR/nba/nba_all.csv')



