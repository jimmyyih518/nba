# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 17:13:02 2020

@author: JZ2018
"""


import numpy as np


#ar1 = np.array([[10, 20, 30],
#                [8, 4, 12],
#                [5, 7, 2]]).T

cats = ['pts', 'rbd', 'ast']
players = ['rondo', 'kcp', 'james', 'davis', 'howard']
pred_possession_split = [0.15,0.15,0.3,0.3,0.1]

ability_dic = {'rondo': {'pts' : 0.100, 'rbd' : 0.104, 'ast' : 0.241},
               'kcp': {'pts' : 0.120, 'rbd' : 0.062, 'ast' : 0.074},
               'james':{'pts' : 0.306, 'rbd' : 0.238, 'ast' : 0.489},
               'davis':{'pts' : 0.345, 'rbd' : 0.290, 'ast' : 0.152},
               'howard':{'pts' : 0.128, 'rbd' : 0.306, 'ast' : 0.043}}


cat_multiplier = {'pts':2.5,
                  'rbd':1,
                  'ast':0.75}
#ar1[players.index('p2'), cats.index('rbd')]
#m1 = 100
#std1 = 10
#a = np.random.normal(m1, std1, 1)
possessions = 80

def goto_player(posessions, players, pred_possession_split):

    p_game = []
    
    for m in range(0, posessions):
        goto = np.random.choice(players, 1, p=pred_possession_split).item()
        p_game.append(goto)
        
    return p_game

#player_possesion = goto_player(5, players, pred_possession_split)

def goto_value(player, cat, ability_dic, cat_multiplier):
    value = ability_dic[player][cat]
    multi = cat_multiplier[cat]
    value = value*multi
    return value

#val = goto_value('james', 'rbd', ability_dic, cat_multiplier)

def run_sim(players, cats, possessions, pred_possession_split ,ability_dic):
    player_possesion = goto_player(possessions, players, pred_possession_split)
    
    i=1
    total_stat = []
    for p in player_possesion:
        for c in cats:
            val = goto_value(p, c, ability_dic, cat_multiplier)
            stats = [p, c, val, i]
            total_stat.append(stats)
            i=i+1
    
    sum_stats = []
    for p in players:
        for c in cats:
            pstat = sum(s[2] for s in total_stat if s[0] == p and s[1] == c)
            temp_stat = [p, c, pstat]
            sum_stats.append(temp_stat)
    
    
    return sum_stats


sim_stats = run_sim(players, cats, possessions, pred_possession_split ,ability_dic)
    
    
    
    
    
    
