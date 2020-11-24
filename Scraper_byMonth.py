# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 13:53:13 2020

@author: JZ2018
"""

#Input Year of season to be scraped:
year = 2016
#Input Directory for output csv files:
output_filedir = 'D:/JZR/nba/boxscores/'

##-----------------------------------------------------------------------------------
#RUN EVERYTHING BELOW

import os
#print(os.getcwd())
from bs4 import BeautifulSoup 
import requests
import pandas as pd

def isNaN(num):
    return num != num

team_dictionary = {
    'Atlanta Hawks': 'Atl', 'Boston Celtics': 'Bos', 
    'Brooklyn Nets': 'Bkn', 'Charlotte Hornets': 'Cha', 
    'Chicago Bulls': 'Chi', 'Cleveland Cavaliers': 'Cle', 
    'Dallas Mavericks': 'Dal', 'Denver Nuggets': 'Den', 
    'Detroit Pistons': 'Det','Golden State Warriors': 'GSW', 
    'Houston Rockets': 'Hou', 'Indiana Pacers': 'Ind',
    'Los Angeles Lakers': 'LAL', 'Los Angeles Clippers': 'LAC', 
    'Memphis Grizzlies': 'Mem', 'Miami Heat': 'Mia', 
    'Milwaukee Bucks': 'Mil', 'Minnesota Timberwolves': 'Min', 
    'New Orleans Pelicans': 'Nor', 'New York Knicks': 'NYK', 
    'Oklahoma City Thunder': 'OKC', 'Orlando Magic': 'Orl', 
    'Philadelphia 76ers': 'Phi', 'Phoenix Suns': 'Pho', 
    'Portland Trail Blazers': 'Por', 'Sacramento Kings': 'Sac', 
    'San Antonio Spurs': 'SAS', 'Toronto Raptors': 'Tor', 
    'Utah Jazz': 'Uta', 'Washington Wizards': 'Was'
}

month_dictionary = {'Jan': '01', 'Feb': '02',  'Mar': '03', 
'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


month_list = ['september','october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']

start_url = "https://www.basketball-reference.com/leagues/NBA_{}_games.html".format(year)

base_url = 'https://www.basketball-reference.com'   #used for formatting each link correctly
month_link_array = []
response = requests.get(start_url)
soup = BeautifulSoup(response.text, 'html.parser')
season = soup.find('h1').text
season = season.strip().split(' ')
season = season[0]
body = soup.findAll('body')
months = body[0].findAll('a', href = True)

for i in months:
    if i.text.lower() in month_list:
        i = (i.text, f'{base_url}{i["href"]}')
        month_link_array.append(i)  #appending the url for each page to scrape
#iterating through each month url to scrape the data

df_columns = ['Date', 'Name', 'Team', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
                   '3P%','FT', 'FTA', 'FT%', 'ORB', 
                   'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+-','Team_Name' ]

def getMonthdata(month, page, df_columns):
    page_tocheck_dict = {'Month': [], 'Url': [], 'Index': []}
    box_link_array = []
    all_dates = []
    page_link_array = []
    page_date_array = []
    response = requests.get(page)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.findAll('tbody')
    box_scores = table[0].findAll('a', href=True)
    for i in box_scores:
        if i.text.strip() == 'Box Score':
            page_link_array.append(f'{base_url}{i["href"]}')
        if ',' in i.text.strip():
            date = i.text.strip()
            date = date.split(', ')
            year = date[2]
            date = date[1].split(' ')
            day = f'0{date[1]}' if len(date[1]) ==1 else date[1]

            mon = month_dictionary[date[0]]
            date = f'{year}{mon}{day}'
            page_date_array.append(date)
    if len(page_link_array) == 0 or len(box_scores)/len(page_link_array) != 4:
        page_tocheck_dict['Url'].append(page)
        page_tocheck_dict['Month'].append(month)
        page_tocheck_dict['Index'].append(len(page_link_array))
    else:
        page_tocheck_dict['Url'].append(page)
        page_tocheck_dict['Month'].append(month)
        page_tocheck_dict['Index'].append(None)
    box_link_array.append(page_link_array)
    all_dates.append(page_date_array)

# =============================================================================
#     df_columns = ['Date', 'Name', 'Team', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
#                    '3P%','FT', 'FTA', 'FT%', 'ORB', 
#                    'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+-','Team_Name' ]
# =============================================================================
    stat_df = pd.DataFrame(columns = df_columns)
    error_df = pd.DataFrame(columns = df_columns)
    for l, d in zip(box_link_array, all_dates):
        #l = box_link_array[0]
        #d = all_dates[0]
        for link, date in zip(l, d):
            #link = l[0]
            #date = d[0]
            #print(f'{link}\n{date}')
            print(f'Currently Scraping {link}')
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
                    
            # first table
            table1 = soup.find('table', {'class': "sortable stats_table"})
            team = table1.text.split('\n')[0]
            parenthesis = team.find('(')
            team = team[:parenthesis - 1]
            #print(team)
            table1 = table1.find('tbody')
            table1 = table1.find_all('tr')
            rows = []
            for row in table1:
                #row = table1[0]
                name = row.findAll('th')[0].text
                cols = row.findAll('td')
                cols = [i.text.strip() for i in cols]
                cols.append(name)
                rows.append(cols)
                for player in rows:
                    #player = rows[0]
                    try:
                        if len(player) < 21:
                            continue
                        else:
                            #player = [0 if i == '' or isNaN(i) else i for i in player]
                            colon = player[0].find(':')
                            time = f'{player[0][:colon]}.{player[0][colon + 1::]}'
                            #print(player, len(player))
                            if team in team_dictionary:
                                return_team = team_dictionary[team]
                            else:
                                return_team = 'NA'
                            player_dic = {'Date': date, 'Name': player[-1], 'Team': return_team, 
                                          'MP': time,'FG': player[1], 'FGA': player[2], 
                                          'FG%': player[3], '3P': player[4], '3PA': player[5],
                                          '3P%': player[6], 'FT': player[7], 'FTA': player[8], 
                                          'FT%': player[9],'ORB': player[10], 
                                          'DRB': player[11], 'TRB': player[12], 
                                          'AST': player[13], 'STL': player[14], 
                                          'BLK': player[15], 'TOV': player[16], 'PF': player[17],
                                          'PTS': player[18], '+-': player[19], 'Team_Name': team}
                            stat_df = stat_df.append(player_dic, ignore_index=True)
                            continue
                    except KeyError:
                        print(str(date) + str(player[-1]) + ':' + 'Key Error')
                        print(len(player))
                        print(player)
                        #print('Key Error')                      
                        continue
                # second table
            table2 = soup.findAll('table', {'class': "sortable stats_table"})
            team = table2[9].text.split('\n')[0]
            parenthesis = team.find('(')
            team = team[:parenthesis - 1]
            table2 = table2[9].find('tbody')
            table2 = table2.find_all('tr')
            rows = []
            for row in table2:
                #row = table2[0]
                name = row.findAll('th')[0].text
                cols = row.findAll('td')
                cols = [i.text.strip() for i in cols]
                cols.append(name)
                rows.append(cols)
            for player in rows:
                #player = rows[0]
                try:
                    if len(player) < 21:
                        #print(player)
                        continue
                    else:
                        #player = [0 if i == '' or isNaN(i) else i for i in player]
                        colon = player[0].find(':')
                        time = f'{player[0][:colon]}.{player[0][colon + 1::]}'
                        if team in team_dictionary:
                            return_team = team_dictionary[team]
                        else:
                            return_team = 'NA'                            
                        #print(player, len(player))
                        player_dic = {'Date': date, 'Name': player[-1], 'Team': return_team, 
                                      'MP': time,'FG': player[1],'FGA': player[2], 
                                      'FG%': player[3], '3P': player[4], 
                                      '3PA': player[5],'3P%': player[6], 'FT': player[7], 
                                      'FTA': player[8], 'FT%': player[9],
                                      'ORB': player[10], 'DRB': player[11], 
                                      'TRB': player[12], 'AST': player[13],
                                      'STL': player[14], 'BLK': player[15], 
                                      'TOV': player[16], 'PF': player[17],
                                      'PTS': player[18], '+-': player[19], 'Team_Name': team}
                        stat_df = stat_df.append(player_dic, ignore_index=True)
                        continue
                except KeyError:
                    print(str(date) + str(player[-1]) + ':' + 'Key Error')
                    print(len(player))
                    print(player)                      
                    #print('Key Error')
                    continue
    return stat_df


#month = month_link_array[0][0]
#page = month_link_array[0][1]  


output_df = pd.DataFrame(columns = df_columns)

for month, page in month_link_array:
    statdf = getMonthdata(month, page, df_columns)
    outfile = output_filedir + 'Season_' + str(season) + str(month) + '_BoxScores'
    statdf.to_csv(f'{outfile}.csv')
    #output_df.to_csv(f'D:/JZR/nba/boxscores/{outfile}.csv')
    #output_df = output_df.append(statdf)



