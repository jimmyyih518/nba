# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 21:53:42 2020

@author: JZ2018
"""


import pandas as pd
import numpy as np

df_raw = pd.read_csv('D:/JZR/nba/nba_all.csv')
with pd.option_context('display.max_columns', 40):
    print(df_raw.describe(include='all'))
    print(df_raw.head())
df_raw.info(verbose=True)

key_cols = ['Name', 'Season']
non_agg_cols = ['WEIGHT', 'Age', 'Days_in_Season', 'Weeks_in_Season',
       'Months_in_Season', 'Cum_MP', 'Cum_FG', 'Cum_FGA', 'Cum_3P', 'Cum_3PA',
       'Cum_FT', 'Cum_FTA', 'Cum_ORB', 'Cum_DRB', 'Cum_TRB', 'Cum_AST',
       'Cum_STL', 'Cum_BLK', 'Cum_TOV', 'Cum_PF', 'Cum_PTS', 'Height_inches', 'POS_0', 'POS_C', 'POS_PF', 'POS_PG', 'POS_SF', 'POS_SG',
       'EXPERIENCE_Yrs', 'Month', 'Before_AllStarWeek', 'Playoff', 'SG_count',
       'PF_count', 'PG_count', 'C_count', 'SF_count']
static_cols = key_cols.copy()
static_cols.extend(non_agg_cols)

df_num = df_raw.select_dtypes(include=['int64', 'float64']).drop(columns = ['Date'])
df_agg = df_num.drop(columns = non_agg_cols)
df_static = df_raw[static_cols]
df_keys = df_raw[key_cols]

df = pd.concat([df_keys.reset_index(drop=True), df_agg], axis = 1)

df_bySeason = df.groupby(key_cols).agg(['mean'])
df_shift1 = df_bySeason.groupby('Name').shift(periods=-1).add_prefix('next1yr_')
df_m1 = df_bySeason.merge(df_shift1, left_index = True, right_index = True, how='left')
df_shift2 = df_bySeason.groupby('Name').shift(periods=-2).add_prefix('next2yr_')
df_m1 = df_m1.merge(df_shift2, left_index = True, right_index = True, how='left')
df_m1.columns = df_m1.columns.droplevel(1)
df_m1 = df_m1.dropna()

x_feat = ['MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB',
       'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+-',
       'next1yr_MP', 'next1yr_FG', 'next1yr_FGA', 'next1yr_FG%', 'next1yr_3P',
       'next1yr_3PA', 'next1yr_3P%', 'next1yr_FT', 'next1yr_FTA',
       'next1yr_FT%', 'next1yr_ORB', 'next1yr_DRB', 'next1yr_TRB',
       'next1yr_AST', 'next1yr_STL', 'next1yr_BLK', 'next1yr_TOV',
       'next1yr_PF', 'next1yr_PTS', 'next1yr_+-']
y_pred = ['next2yr_PTS']
train_cols = y_pred.copy()
train_cols.extend(x_feat)
dt_train = df_m1[train_cols]
labels = np.array(dt_train[y_pred])
features = np.array(dt_train.drop(columns = y_pred))
feature_list = list(dt_train.drop(columns = y_pred).columns)

from sklearn.model_selection import train_test_split
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)

print('Training Features Shape:', train_features.shape)
print('Training Labels Shape:', train_labels.shape)
print('Testing Features Shape:', test_features.shape)
print('Testing Labels Shape:', test_labels.shape)

from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
rf.fit(train_features, train_labels)

predictions = rf.predict(test_features)
errors = abs(predictions - test_labels)
print(round(np.mean(errors),2))

import matplotlib.pyplot as plt
import scipy as sp
plt.style.use('seaborn-whitegrid')
plt.plot(predictions, test_labels, 'o', color = 'red')
plt.xlabel('Predictions')
plt.ylabel('Actuals')
test_labels_flat = test_labels.mean(axis=1)
linreg = sp.stats.linregress(predictions, test_labels_flat)
#plt.plot(predictions, linreg.intercept + linreg.slope*test_labels_flat, 'r')
plt.plot(np.unique(test_labels_flat), np.poly1d(np.polyfit(test_labels_flat, predictions, 1))(np.unique(test_labels_flat)))
plt.text(16, 10, 'R-squared = %0.2f' % linreg.rvalue)
plt.show()


importances = rf.feature_importances_
indices = np.argsort(importances)
plt.title('Feature Importances')
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [feature_list[i] for i in indices])
plt.tick_params(axis='both', which='major', labelsize=5)
plt.xlabel('Relative Importance')
plt.show()

import shap
train_df = pd.DataFrame(data = np.concatenate((train_features, train_labels), axis=1), columns = train_cols)

# Create Tree Explainer object that can calculate shap values
explainer = shap.TreeExplainer(rf)
# Calculate Shap values
choosen_instance = test_features[1]
shap_values = explainer.shap_values(choosen_instance)
shap.initjs()
shap.force_plot(explainer.expected_value[1], shap_values[1], choosen_instance)


shap_values = shap.TreeExplainer(rf).shap_values(train_df)
shap.summary_plot(shap_values, train_df)

