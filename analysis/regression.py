import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import mannwhitneyu, linregress
import matplotlib.pyplot as plt
import os
import seaborn as sns

df = pd.read_csv("../data/cleaned_data.csv")

# This is only to keep pages that Have a vital level
df_filtered = df[df['vital_level'] > 0].copy()

df_no0 = df_filtered[df_filtered['links_away'] != 0].copy()

# OLS TEST 
X = sm.add_constant(df_no0['links_away']) # column of 1s to estimate an intercept
y = df_no0['vital_level']
ols = sm.OLS(y, X).fit()
print("OLS without links_away == 0")
print(ols.summary())

# Print explicit OLS direction for hypothesis
coef = ols.params.get('links_away', np.nan)
pval = ols.pvalues.get('links_away', np.nan)

# Mann–Whitney U (one‑tailed, Near > Far) using separated quartiles
q25 = df_no0['links_away'].quantile(0.25)
q75 = df_no0['links_away'].quantile(0.75)
near = df_no0.loc[df_no0['links_away'] <= q25, 'vital_level']
far  = df_no0.loc[df_no0['links_away'] >= q75, 'vital_level']

res_mw = mannwhitneyu(near, far, alternative='greater')  
print(f"Mann–Whitney p={res_mw.pvalue}")

# Group by links_away and calculate mean vital_level
grouped = df_no0.groupby('links_away')['vital_level'].mean().reset_index()


slope, intercept, r_value, p_value, std_err = linregress(grouped['links_away'], grouped['vital_level'])


plt.figure(figsize=(10,6))
sns.barplot(x='links_away', y='vital_level', data=grouped, color='skyblue')


x_vals = np.array(grouped['links_away'])
y_vals = intercept + slope * x_vals
plt.plot(x_vals, y_vals, color='red', linewidth=2)

plt.xlabel('Hyperlinks Away')
plt.xticks(rotation=30)
plt.ylabel('Mean Vital Level')
plt.title('Mean Vital Level vs. Hyperlinks Away from Philosophy (x=0 removed)')
plt.savefig('./plots/mean_vital_by_step_no0.png')
plt.close()

