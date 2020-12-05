rm(list=ls())
gc()
cat("\014")

library(data.table)
library(dplyr)
library(broom)
`%nin%` = Negate('%in%')
Fun_ReadBox = function(boxdir){
  for(f in list.files(boxdir)){
    tempdt = fread(paste0(boxdir,f))
    season = gsub('Season_', '', f)
    season = gsub('_BoxScores.csv', '', season)
    slist = unlist(strsplit(season, split = '-'))
    season_startYr = slist[1]
    season_endYr = slist[2]
    season_endYr = gsub('[a-zA-z]', '', season_endYr)
    season_endYr = paste0('20', season_endYr)
    tempdt$season_startYr = as.integer(season_startYr)
    tempdt$season_endYr = as.integer(season_endYr)
    if(exists('outdt')){
      outdt = rbind(outdt, tempdt)
    } else {
      outdt = tempdt
    }
  }

  names(outdt) = make.names(names(outdt))
  return(outdt)
}
FUN_heightconv = function(x){
  xs = unlist(strsplit(x, split = '-'))
  out = as.numeric(xs[1]) + as.numeric(xs[2])*12
  return(out)
}
FUN_seasonyear = function(x){
  xs = unlist(strsplit(x, split = '-'))
  return(as.integer(xs[1]))
}
outlier_rm = function(df, coloutier) {
  outl = rep( NA, length(df[[coloutier]]))
  detr = c( 0, diff(df[[coloutier]]))
  ix = detr < -2*IQR( detr, na.rm = T)
  df$outliers = ifelse(ix==FALSE, NA, df[[coloutier]])
  return(df)
}
FUN_Readteam = function(teamdir){
  for(f in list.files(teamdir)){
    tempdt = fread(paste0(teamdir,f))
    season = gsub('Season_', '', f)
    season = gsub('_teamInfo.csv', '', season)
    slist = unlist(strsplit(season, split = '-'))
    season_startYr = slist[1]
    season_endYr = paste0('20',slist[2])
    tempdt$season_startYr = as.integer(season_startYr)
    tempdt$season_endYr = as.integer(season_endYr)
    if(exists('outdt')){
      outdt = rbind(outdt, tempdt)
    } else {
      outdt = tempdt
    }
  }

  return(outdt)
}
FUN_zscore = function(x){
  if(is.character(x)){
    z = x
  } else {
    z = (x - mean(x, na.rm=T)) / sd(x, na.rm=T)
  }
  
  return(z)
}
FUN_BoxTeamSummary = function(dtbox, dtteam, rm_year){
  dt = dtbox %>%
    filter(season_endYr %nin% rm_year) %>%
    group_by(season_endYr) %>%
    summarise_at(vars(c('Name', names(catcols))), .funs ='FUN_zscore') %>%
    ungroup() %>%
    group_by(Name, season_endYr) %>%
    summarise_at(vars(names(catcols)), .funs = 'mean') %>%
    replace(is.na(.),0) %>%
    arrange(Name, season_endYr) %>%
    left_join(., dtteam, by=c('Name' = 'PLAYER', 'season_endYr' = 'season_endYr')) 
  
  return(dt)
  
}
FUN_tidyLM1 = function(dt, yvar, xvar){
  names(dt)[names(dt)==yvar] = 'lmY'
  names(dt)[names(dt)==xvar] = 'lmX'
  dt_lm = dt %>%
    group_by(Name) %>%
    do(model = lm(lmY~lmX, data = .))
  
  for(r in 1:nrow(dt_lm)){
    mod = dt_lm[r, ]$model
    mod = mod[[1]]
    tidydt = as.data.frame(tidy(mod))
    tidydt$Name = as.character(dt_lm[r,'Name'])
    if(exists('outdt')){
      outdt = rbind(outdt, tidydt)
    } else {
      outdt = tidydt
    }
  }
  
  outdt = outdt %>% filter(term == 'lmX') %>% select(Name, estimate)
  names(outdt) = c('Name', 'Trend_Slope')
  outdt = outdt %>%
    mutate(Trend_Slope = ifelse(is.na(Trend_Slope), mean(Trend_Slope, na.rm=T), Trend_Slope))
  return(outdt)
}
FUN_LMCat = function(dt, catlist, season_endYr, dt_pred){
  cat_models = list()
  for(cat in catlist){
    dt_lm = FUN_tidyLM1(dt, cat, season_endYr) 
    names(dt)[names(dt) == cat] = 'PredVal'
    modeldt = dt %>% group_by(Name) %>%
      summarise(AvgStat = mean(PredVal), 
                EXPERIENCE = max(as.integer(EXPERIENCE), na.rm=T),
                Variance = max(PredVal, na.rm = T) - min(PredVal, na.rm = T)) %>%
      left_join(dt_lm) %>%
      mutate(EXPERIENCE = ifelse(is.infinite(EXPERIENCE), 0, EXPERIENCE)) %>%
      left_join(dt_pred[,c('Name', cat)]) %>%
      na.omit()
    lmFormula = paste0(cat, '~AvgStat+EXPERIENCE+Variance+Trend_Slope')
    lm1 = lm(lmFormula, data = modeldt)
    cat_models[[cat]] = lm1
    pred_name = paste0('Pred_', cat)
    outputdt = modeldt
    outputdt[[pred_name]] = predict(lm1, newdata = outputdt)
    names(outputdt)[names(outputdt)=='AvgStat'] = paste0('Avg_',cat)
    names(outputdt)[names(outputdt)=='Variance'] = paste0('Var_',cat)
    names(outputdt)[names(outputdt)=='Trend_Slope'] = paste0('Tslope_',cat)
    
    if(exists('outputdt2')){
      outputdt2 = left_join(outputdt2, outputdt)
    } else {
      outputdt2 = outputdt
    }
    names(dt)[names(dt) == 'PredVal'] = cat
  }
  output = list()
  output$cat_models = cat_models
  output$dt_pred = outputdt2
  return(output)
}
FUN_CatPred = function(dt_new, catlist, lm_mods, lmdt){
  
  for(cat in catlist){
    slope_name = paste0('Tslope_', cat)
    dt_lm = select(lmdt, Name, all_of(slope_name))
    lmMod = lm_mods[[cat]]
    names(dt_new)[names(dt_new) == cat] = 'PredVal'
    modeldt = dt_new %>% group_by(Name) %>%
      summarise(AvgStat = mean(PredVal, na.rm=T), 
                EXPERIENCE = max(as.integer(EXPERIENCE), na.rm=T),
                Variance = max(PredVal, na.rm = T) - min(PredVal, na.rm = T)) %>%
      left_join(dt_lm) %>%
      mutate(EXPERIENCE = ifelse(is.infinite(EXPERIENCE), 0, EXPERIENCE)) %>%
      na.omit()
    names(modeldt)[names(modeldt) == slope_name] = 'Trend_Slope'  
    pred_name = paste0('Pred_', cat)
    modeldt[[pred_name]] = predict(lmMod, newdata = modeldt)
    
    outputdt = modeldt
    names(outputdt)[names(outputdt)=='AvgStat'] = paste0('Avg_',cat)
    names(outputdt)[names(outputdt)=='Variance'] = paste0('Var_',cat)
    names(outputdt)[names(outputdt)=='Trend_Slope'] = paste0('Tslope_',cat)
    
    if(exists('outputdt2')){
      outputdt2 = left_join(outputdt2, outputdt)
    } else {
      outputdt2 = outputdt
    }
    names(dt_new)[names(dt_new) == 'PredVal'] = cat
  }
  return(outputdt2)
}
catcols = data.frame('X3P' = 3, 
                     'X3PA' = -1, 
                     'FT' = 1, 
                     'FTA' = -0.75, 
                     'FGA' = -0.45, 
                     'FG' = 1, 
                     'PTS' = 1,
                     'TRB' = 2, 
                     'AST' = 2, 
                     'STL' = 3, 
                     'BLK' = 3, 
                     'TOV' = -3
                )

dtbox = Fun_ReadBox('D:/JZR/nba/boxscores/') 
dtteam = FUN_Readteam('D:/JZR/nba/teaminfo/') %>% distinct(PLAYER, season_endYr, .keep_all = T) %>% select(-V1)
dt = FUN_BoxTeamSummary(dtbox, dtteam, rm_year = 2020)
dt_pred = FUN_BoxTeamSummary(dtbox, dtteam, rm_year = c(2010:2019))

#loop through variables to lm


lm_output = FUN_LMCat(dt, names(catcols), 'season_endYr', dt_pred)
lmdt = lm_output$dt_pred
lm_mods = lm_output$cat_models

dt_new = FUN_BoxTeamSummary(dtbox, dtteam, rm_year = 2022)
PredNew = FUN_CatPred(dt_new, names(catcols), lm_mods, lmdt)

dt_newPred = PredNew %>%
  select(Name, contains('Pred_')) %>%
  rename_at(vars(contains('Pred_')),.funs = funs(sub('Pred_', '', .))) %>%
  mutate(FGPct = FG / FGA,
         FTPct = FT / FTA) %>%
  mutate(FGPct = ifelse(FGPct > 3, 3, FGPct),
         FTPct = ifelse(FTPct > 3, 3, FTPct)) %>%
  mutate(FGPct = ifelse(FGPct < -3, -3, FGPct),
         FTPct = ifelse(FTPct < -3, -3, FTPct))


all_cats = c('PTS','X3P', 'TRB','AST','STL','BLK','FGPct','FTPct','TOV')
cat_vals = c(1, 2, 2, 2, 2.5, 2.5, 1, 1, 0)
cat_df = data.frame(cat = all_cats, val = cat_vals)


dt = FUN_BoxTeamSummary(dtbox, dtteam, rm_year = c(2010:2019)) %>%
  select(Name, all_of(names(catcols))) %>%
  mutate(FGPct = FG / FGA,
         FTPct = FT / FTA) %>%
  mutate(FGPct = ifelse(FGPct > 3, 3, FGPct),
         FTPct = ifelse(FTPct > 3, 3, FTPct)) %>%
  mutate(FGPct = ifelse(FGPct < -3, -3, FGPct),
         FTPct = ifelse(FTPct < -3, -3, FTPct)) %>%
  select(Name, all_of(cat_df$cat)) %>%
  rename_at(vars(all_of(cat_df$cat)), .funs=funs(paste0('Prev_', .)))
  

dt_newPred2 = dt_newPred %>%
  rename_at(vars(all_of(cat_df$cat)), .funs=funs(paste0('Pred_', .))) %>%
  left_join(., dt, by='Name')



for(cat in cat_df$cat){
  pred_name = paste0('Pred_', cat)
  prev_name = paste0('Prev_', cat)
  if(cat %in% c('FGPct', 'FTPct')){
    dt_newPred2[[cat]] = dt_newPred2[[pred_name]]*0.3 + dt_newPred2[[prev_name]]*0.7
  } else {
    dt_newPred2[[cat]] = dt_newPred2[[pred_name]]*0.5 + dt_newPred2[[prev_name]]*0.5
  }
  
}

dt_newPred3 = dt_newPred2[, names(dt_newPred2) %in% c('Name', cat_df$cat)]
range01 <- function(x){(x-min(x))/(max(x)-min(x))}
dt_newPred3$FGPct = range01(dt_newPred3$FGPct)
dt_newPred3$FTPct = range01(dt_newPred3$FTPct)
dt_newPred3$RVal = 0


for(cat in cat_df$cat){
  curr_val = cat_df[cat_df$cat==cat,]$val
  dt_newPred3$RVal = dt_newPred3$RVal + dt_newPred3[[cat]]*curr_val
}

Inj_Players = c('Kristaps PorziÅ†Ä£is', 'Jonathan Isaac', 'Kris Dunn', 'Jaren Jackson',
                'Jeremy Lamb', 'Dwight Powell', 'Tony Snell', 'Zach Collins', 'Justise Winslow')

dt_newPred3 = dt_newPred3 %>% arrange(desc(RVal)) %>%
  filter(Name %nin% Inj_Players) %>%
  mutate(Rank = row_number())

team_dt = data.frame(Name = '',Pos = '', DraftPosition=0,DraftRound = 0)
tot_teams = 16
tot_rounds = 12
yahoo_dt = readxl::read_xlsx('D:/JZR/nba/yahoo rank_2.xlsx')
names(yahoo_dt) = c('ProjRank','XRank','Name')
dt_teamPOS = dtteam[, c('PLAYER', 'POS')] %>%
  distinct(PLAYER, .keep_all = T)
d3 = dt_newPred3 %>%
  left_join(., yahoo_dt, by=c('Name')) %>%
  left_join(., dt_teamPOS, by=c('Name' = 'PLAYER')) %>%
  rename(Pos = POS)
#d3a = left_join(yahoo_dt, dt_newPred3, by=c('Name'))

for(d in 1:tot_teams){
  players_selected = c()
  my_team = data.frame(Name = '',Pos = '')
  dt_sel = d3
  
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
  my_team$DraftRound = row.names(my_team)
  my_team$DraftRound = as.integer(my_team$DraftRound)-1
  team_dt = rbind(team_dt, my_team)
}


team_dt = team_dt[2:nrow(team_dt),]
team_dt = left_join(team_dt, d3[,c('Name','RVal')])
team_sum = team_dt %>% group_by(DraftPosition) %>%
  summarise(Tot_Val = sum(RVal))
write.csv(team_dt, 'D:/JZR/nba/optDraft2.csv', row.names = F)
# fwrite(dt_newPred, "D:/JZR/nba/dt_newpred.csv")
# dt_newPred = fread("D:/JZR/nba/dt_newpred.csv")
# BBMdt = readxl::read_xls('D:/JZR/nba/BBM/BBM_PlayerRankings19-20.xls')
# 
# dtjoin = dt_newPred %>%
#   left_join(., BBMdt, by=c('Name'))


