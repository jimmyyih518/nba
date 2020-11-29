library(data.table)
library(dplyr)

dt = fread("D:/JZR/nba/nba_all.csv")
d1 = dt[dt$Name=='Anthony Davis',]

FUN_heightconv = function(x){
  xs = unlist(strsplit(x, split = '-'))
  out = as.numeric(xs[1]) + as.numeric(xs[2])*12
  return(out)
}

d1s = dt %>%
  #mutate(Before_AllStarWeek == 0) %>%
 group_by(Name, Season, Before_AllStarWeek, Playoff) %>% summarise_all(.funs='max')

d1a = d1s %>% filter(Before_AllStarWeek==0 & Playoff==0) %>%
  select(Name, Season, POS, HEIGHT, WEIGHT, EXPERIENCE_Yrs, Age, starts_with('Cum_'), ends_with('_count'))


d1a1 = d1a %>% ungroup() %>%
  group_by(Name, Before_AllStarWeek) %>%
  mutate(Cum_MP_prev = lag(Cum_MP),
         Cum_FG_prev = lag(Cum_FG),
         Cum_FGA_prev = lag(Cum_FGA),
         Cum_3P_prev = lag(Cum_3P),
         Cum_3PA_prev = lag(Cum_3PA),
         Cum_FT_prev = lag(Cum_FT),
         Cum_FTA_prev = lag(Cum_FTA),
         Cum_ORB_prev = lag(Cum_ORB),
         Cum_DRB_prev = lag(Cum_DRB),
         Cum_TRB_prev = lag(Cum_TRB),
         Cum_AST_prev = lag(Cum_AST),
         Cum_STL_prev = lag(Cum_STL),
         Cum_BLK_prev = lag(Cum_BLK),
         Cum_TOV_prev = lag(Cum_TOV),
         Cum_PF_prev = lag(Cum_PF),
         Cum_PTS_prev = lag(Cum_PTS))


catcols = c('Cum_3P', 'Cum_FT', 'Cum_TRB', 'Cum_AST', 'Cum_STL', 'Cum_BLK', 'Cum_TOV', 'Cum_PTS')
factors = c(1, 0.3, 1.25, 1.5, 2, 2, -1, 1)
dcat = data.frame(row.names = c('mean', 'sd'))

meanval = c()
stdval = c()

for(cat in catcols){
  meanval = append(meanval, mean(d1a1[[cat]]))
  stdval = append(stdval, sd(d1a1[[cat]]))
}

catdic = data.frame('cat' = catcols, 'mean' = meanval, 'std' = stdval, 'factor' = factors)  

d1a1$Cum_rank = 0
for(cat in catcols){
  d1a1$calc = (d1a1[[cat]] - catdic[catdic$cat==cat, 'mean']) / catdic[catdic$cat==cat, 'std'] * catdic[catdic$cat==cat, 'factor']
  d1a1$Cum_rank = d1a1$Cum_rank + d1a1$calc
  d1a1 = select(d1a1, -calc)
}

d1a1 = d1a1 %>% ungroup() %>%
  group_by(Name, Before_AllStarWeek) %>%
  mutate(Cum_rank_prev = lag(Cum_rank)) %>%
  na.omit()
 
train_vars = c("Cum_rank_prev","SG_count","PF_count","PG_count","C_count","SF_count",       
               "Cum_MP_prev","Cum_FG_prev", "Cum_FGA_prev", "Cum_3P_prev", "Cum_3PA_prev", "Cum_FT_prev" ,      
               "Cum_FTA_prev","Cum_ORB_prev","Cum_DRB_prev" , "Cum_TRB_prev", "Cum_AST_prev", "Cum_STL_prev" ,     
               "Cum_BLK_prev" ,"Cum_TOV_prev" , "Cum_PF_prev" , "Cum_PTS_prev","WEIGHT", "EXPERIENCE_Yrs", "Age",
               "POS", "HEIGHT")

pred_var = "Cum_rank"

modeldt = d1a1[,c(pred_var,train_vars)]
modeldt = modeldt[modeldt$POS != '0',]
modeldt$HEIGHT = mapply(FUN_heightconv, modeldt$HEIGHT)
samprows = sort(sample(nrow(modeldt), as.integer(nrow(modeldt)*0.75)))
traindt = modeldt[row.names(modeldt) %in% samprows,]
trainsave = traindt
testdt = modeldt[!(row.names(modeldt) %in% samprows),]

xdt = traindt[,train_vars]
ydt = traindt[,pred_var]




#lm_fmla = paste(rfe_vars, collapse = '+')
#lm_fmla = paste(pred_var, '~', lm_fmla, sep='')
#lm1 = lm(lm_fmla, data=traindt)
library(leaps)
leapsc2 = regsubsets(Cum_rank~., data = traindt, method = 'exhaustive')
summary.leapsc2 <- summary(leapsc2)
leaptabc2<-data.frame(summary.leapsc2$which[which.max(summary.leapsc2$adjr2),])
leaptabc2 <- add_rownames(leaptabc2, "Variable")
colnames(leaptabc2) <- c("Variable","InOut")
leaptabc2 <- leaptabc2%>%filter(InOut==TRUE)
leaptabc2 <- leaptabc2[2:nrow(leaptabc2),]
leaptabc3 <- leaptabc2[!grepl('POS',leaptabc2$Variable),]
LMfmla <- paste(append('POS',leaptabc3$Variable), collapse = "+")
LMfmla <- paste(pred_var, "~", LMfmla)
lmModel <- lm(LMfmla, data=traindt) 

library(caret)
set.seed(123)
# ctrl = rfeControl(functions = rfFuncs,
#                   method = 'repeatedcv',
#                   repeats = 5)
# rfe1 = rfe(Cum_rank~., data = traindt, sizes = c(5:15), metric = "RMSE", rfeControl = ctrl)
# 
# rfe_vars = rfe1$optVariables
#rfe_vars = append(rfe_vars,c('Age', 'HEIGHT', 'WEIGHT'))
names(traindt)[names(traindt)==pred_var] <- 'Pred_Label'

controlRFE <- rfeControl(functions=rfFuncs, method="cv", number =10)
resultRFE <- rfe(Pred_Label~., data = traindt, sizes=c(1:(ncol(traindt)-1)), rfeControl = controlRFE)
plot(resultRFE, type=c("g", "o"))
rfe_vars = resultRFE$optVariables
opt_vars = rfe_vars
opt_vars = append('Pred_Label', opt_vars)
opt_dt = traindt[,names(traindt) %in% opt_vars]

#library(randomForest)
#rf1 = randomForest(Pred_Label~., data = opt_dt, importance = TRUE)

tctrl = trainControl(method = 'repeatedcv',repeats = 3, number = 5)
rf2 = train(Pred_Label ~ ., data=opt_dt, method="cforest", preProcess = "scale", trControl = tctrl)
#mars1 = train(Pred_Label ~ ., data=opt_dt, method="earth", preProcess = "scale", trControl = tctrl)
bm1 <- train(Pred_Label ~ ., data=opt_dt, method="brnn", preProcess = "scale", trControl = tctrl)
nn1 =  train(Pred_Label ~ ., data=opt_dt, method="gbm", preProcess = "scale", trControl = tctrl)


trainsave$Type = 'TRAIN'
testdt$Type = 'TEST'
finaldt = rbind(trainsave, testdt)
names(finaldt)[names(finaldt)==pred_var] <- 'Pred_Label'
finaldt$pred1 = predict(rf2, newdata = finaldt)
finaldt$pred2 = predict(lmModel, newdata = finaldt)
finaldt$pred3 = predict(bm1, newdata = finaldt)
finaldt$pred4 = predict(nn1, newdata = finaldt)

finaldt$avgpred = (finaldt$pred1+ finaldt$pred2+ finaldt$pred3+ finaldt$pred4)/4


finaldt$Type = as.factor(finaldt$Type)
par(mfrow=c(2,2))
plot(finaldt$pred1,finaldt$Pred_Label,  col = finaldt$Type, pch = 19, xlab = 'Predicted', 
     ylab = paste('Actual',pred_var), main = 'RandomForest')
text(x=-5, y=20, labels = paste('R Squared =',
      round(summary(lm(Pred_Label~pred1,data = finaldt[finaldt$Type=='TEST',]))$r.squared, 3)))

plot(finaldt$pred2, finaldt$Pred_Label, col = finaldt$Type, pch = 19, xlab = 'Predicted',
     ylab = paste('Actual',pred_var), main = 'LinearRegression')
text(x=-5, y=20, labels = paste('R Squared =',
      round(summary(lm(Pred_Label~pred2, data = finaldt[finaldt$Type=='TEST',]))$r.squared, 3)))

plot(finaldt$pred3,finaldt$Pred_Label,  col = finaldt$Type, pch = 19, xlab = 'Predicted',
     ylab = paste('Actual',pred_var), main = 'Bayesian')
text(x=-5, y=20, labels = paste('R Squared =',
      round(summary(lm(Pred_Label~pred3, data = finaldt[finaldt$Type=='TEST',]))$r.squared, 3)))

plot(finaldt$pred4, finaldt$Pred_Label, col = finaldt$Type, pch = 19, xlab = 'Predicted', 
     ylab = paste('Actual',pred_var), main = 'Boosted Tree')
text(x=-5, y=20, labels = paste('R Squared =',
      round(summary(lm(Pred_Label~pred4, data = finaldt[finaldt$Type=='TEST',]))$r.squared, 3)))

#summary(lmModel)
#lmtest = lm(Cum_rank ~ Cum_rank_prev+C_count+SF_count+Cum_FG_prev+Cum_FGA_prev+Cum_FTA_prev+Cum_PF_prev+Age, data = trainsave)
#summary(lmtest)

FUN_seasonyear = function(x){
  xs = unlist(strsplit(x, split = '-'))
  return(as.integer(xs[1]))
}

newpred = d1a1 %>%
  group_by(Name) %>%
  #filter(EXPERIENCE_Yrs == max(EXPERIENCE_Yrs)) %>%
  filter(POS != 0)
newpred$season_year = mapply(FUN_seasonyear, newpred$Season)
newpred = newpred %>%
  group_by(Name) %>%
  filter(season_year == max(season_year))

newpred = newpred %>% mutate(Cum_MP_prev = Cum_MP,
                               Cum_FG_prev = Cum_FG,
                               Cum_FGA_prev = Cum_FGA,
                               Cum_3P_prev = Cum_3P,
                               Cum_3PA_prev =Cum_3PA,
                               Cum_FT_prev = Cum_FT,
                               Cum_FTA_prev = Cum_FTA,
                               Cum_ORB_prev = Cum_ORB,
                               Cum_DRB_prev = Cum_DRB,
                               Cum_TRB_prev = Cum_TRB,
                               Cum_AST_prev = Cum_AST,
                               Cum_STL_prev = Cum_STL,
                               Cum_BLK_prev = Cum_BLK,
                               Cum_TOV_prev = Cum_TOV,
                               Cum_PF_prev = Cum_PF,
                               Cum_PTS_prev = Cum_PTS,
                               Cum_rank_prev = Cum_rank) %>%
  mutate(Age = Age+2020-season_year,
         EXPERIENCE_Yrs = EXPERIENCE_Yrs + 2020 - season_year) 
newpred$pred_rank = predict(lmModel, newdata = newpred)
newpred = newpred %>% arrange(desc(pred_rank))
fwrite(newpred, "D:/JZR/nba/predictions.csv")
