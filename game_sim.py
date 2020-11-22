import numpy as np


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

possessions = 80

def goto_player(posessions, players, pred_possession_split):

    p_game = []
    
    for m in range(0, posessions):
        goto = np.random.choice(players, 1, p=pred_possession_split).item()
        p_game.append(goto)
        
    return p_game



def goto_value(player, cat, ability_dic, cat_multiplier):
    value = ability_dic[player][cat]
    multi = cat_multiplier[cat]
    value = value*multi
    return value



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
    
    
    
    
    
    
