library(readxl)
library(dplyr)
dt_raw = read_xls('D:/JZR/nba/BBM_PlayerRankings.xls')
yahoo_dt = read.csv('D:/JZR/nba/yahoo rank.csv')
names(yahoo_dt) = c('ProjRank','XRank','Name')
dt = left_join(dt_raw, yahoo_dt, by='Name')
draft_pos = 5
tot_teams = 16

const_def = data.frame(pos = c('PG','SG','G','SF','PF','F','C','Util','BN'),
                       TotPlayer = c(1,1,1,1,1,1,1,3,2)
                       )

names(dt) = make.names(names(dt))
all_cats = c('pV','X3V', 'rV','aV','sV','bV','fg.V','ft.V','toV')
cat_vals = c(1, 2, 2, 2, 2.5, 2.5, 1.5, 1.5, -2.5)

cat_df = data.frame(cat = all_cats, val = cat_vals)

rounds = unique(dt$Round)
tot_rounds = sum(const_def$TotPlayer)

dt$RVal = 0
for(cat in cat_df$cat){
  curr_val = cat_df[cat_df$cat==cat,]$val
  dt$RVal = dt$RVal + dt[[cat]]*curr_val
}



dt = dt %>% filter(is.na(Inj)) %>% arrange(desc(RVal))
`%nin%` = Negate('%in%')
team_dt = data.frame(Name = '',Pos = '', DraftPosition=0)
for(d in 1:tot_teams){
  players_selected = c()
  my_team = data.frame(Name = '',Pos = '')
  dt_sel = dt
  
  for(i in 1:tot_rounds){
    dt_sel = dt_sel[dt_sel$Name %nin% players_selected,]
    
    tempdt = dt_sel %>%
      arrange(XRank) %>%
      slice(1:tot_teams)
    
    players_selected = append(players_selected, tempdt$Name)
    if( i %% 2 == 0){
      temp_draft_pos = tot_teams - d
    } else {
      temp_draft_pos = d
    }
    tempdt2 = tempdt %>%
      arrange(XRank) %>%
      slice(temp_draft_pos : n()) %>%
      arrange(desc(RVal))
    
    
    top_sel = tempdt2 %>%
      slice(1)
    
    my_select = data.frame(Name = top_sel$Name, Pos = top_sel$Pos)
    my_team = rbind(my_team, my_select)
    
    
    
  }
  my_team = my_team[2:nrow(my_team),]
  my_team$DraftPosition = d
  team_dt = rbind(team_dt, my_team)
}


team_dt = team_dt[2:nrow(team_dt),]

write.csv(team_dt, 'D:/JZR/nba/optDraft.csv', row.names = F)
