library(data.table)

dt = fread('D:/JZR/nba/Season(2019-20).csv')

team = c('LeBron James', 'Anthony Davis', 'Rajon Rondo', 'Kentavious Caldwell-Pope', 'Dwight Howard')
cats = c('PTS', 'TRB', 'AST')

for(p in team){
  tempdt = dt[dt$Name == p]
  for(a in cats){
    a_mean = mean(tempdt[[a]])
    a_std = sd(tempdt[[a]])
    tempout = data.frame(Name = p,
                         Category = a,
                         Mean = a_mean,
                         StDev = a_std)
    if(exists('sum_stat')){
      sum_stat = rbind(sum_stat, tempout)
    } else {
      sum_stat = tempout
    }
  }

}

sum_stat$StDev_pct = sum_stat$StDev/sum_stat$Mean
sumlist = list()
for(a in cats){
  tempsum = sum_stat[sum_stat$Category == a,]
  catsum = sum(tempsum$Mean)
  sumlist[[a]] = catsum
}
sumlistdf = as.data.frame(sumlist)
sumlistdf = as.data.frame(t(sumlistdf))
setDT(sumlistdf, keep.rownames = T)
names(sumlistdf) = c('Category', 'Category_Sum')

sum_stat = merge(sum_stat, sumlistdf)
sum_stat$Mean_pct = sum_stat$Mean / as.numeric(sum_stat$Category_Sum)
