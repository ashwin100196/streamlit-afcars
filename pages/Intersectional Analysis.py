import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

# Read in the data
df = pd.read_csv("master.csv")

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Create a dropdown for selecting a school within the district
selected_school = st.sidebar.selectbox('Select a School:', df[df['District Name'] == district]['School Name'].unique())

# Filter the dataframe
df = df[(df['District Name'] == district) & (df['School Name'] == selected_school)]

df['year'] = df['year'].apply(lambda y: str(y-1) + '-' + str(y)[2:])

# Create a list of years
years = df['year'].unique()
year = st.sidebar.selectbox('Select a year', years)

# Filter the dataframe
df = df[df['year'] == year]

# Calculation of total disciplined and total eligible counts by race
df_dis_total = df[df['Students w/ Disabilities'].isnull() & df['English Learners'].isnull() & df['Low Income'].isnull()]
disciplined_total = df_dis_total.groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Total Disciplined')
total_eligible = df_dis_total.groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Total Eligible')

# Calculation of total disabled students disciplined and total disabled studnets eligible counts by race
df_disable = df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'].isnull())]
disciplined_disabled = df_disable.loc[df_disable['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Disabled Disciplined')
total_disabled = df_disable.loc[df_disable['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Disabled Total')

# Calculation of total english learner students disciplined and total english learner studnets eligible counts by race
df_eng = df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'] == 'English Learner') & (df['Low Income'].isnull())]
disciplined_eng = df_eng.loc[df_eng['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='English Learner Disciplined')
total_eng = df_eng.loc[df_eng['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='English Learner Total')

# Calculation of total low income students disciplined and total income students eligible counts by race
df_lowinc = df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'] == 'Low Income')]
disciplined_lowinc = df_lowinc.loc[df_lowinc['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Low Income Disciplined')
total_lowinc = df_lowinc.loc[df_lowinc['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Low Income Total')

# Calculation of low income in disciplined disabled students and low income in total disabled students count and use it fro vice verse
df_low_in_dis = df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'] == 'Low Income')]
low_in_disciplined_dis = df_low_in_dis.loc[df_low_in_dis['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Low Income in Disciplined disabled')
total_low_in_disciplined_dis = df_low_in_dis.loc[df_low_in_dis['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Low Income in Total disabled')


# Calculation of english learner in disciplined disabled students and english in total disabled students count and use it for vice versa
df_eng_in_dis = df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'] == 'English Learner') & (df['Low Income'].isnull())]
eng_in_disciplined_dis = df_eng_in_dis.loc[df_eng_in_dis['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='English Learner in Disciplined disabled')
total_eng_in_disciplined_dis = df_eng_in_dis.loc[df_eng_in_dis['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='English in Total disabled')

# Calculation of english learner in disciplined low income students and english in total low income students count and use it for vice versa
df_eng_in_low = df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'] == 'English Learner') & (df['Low Income'] == 'Low Income')]
eng_in_disciplined_low = df_eng_in_low.loc[df_eng_in_low['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Low Income in English learner')
total_eng_in_disciplined_low = df_eng_in_low.loc[df_eng_in_low['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Low Income in total English Learner')

# Merge all your dataframes on 'Race/Ethnicity'
merged_df = disciplined_total.merge(
    total_eligible, on='Race/Ethnicity', how='left'
).merge(
    disciplined_disabled, on='Race/Ethnicity', how='left'
).merge(
    total_disabled, on='Race/Ethnicity', how='left'
).merge(
    disciplined_eng, on='Race/Ethnicity', how='left'
).merge(
    total_eng, on='Race/Ethnicity', how='left'
).merge(
    disciplined_lowinc, on='Race/Ethnicity', how='left'
).merge(
    total_lowinc, on='Race/Ethnicity', how='left'
).merge(
    low_in_disciplined_dis, on='Race/Ethnicity', how='left'
).merge(
    total_low_in_disciplined_dis, on='Race/Ethnicity', how='left'
).merge(
    eng_in_disciplined_dis, on='Race/Ethnicity', how='left'
).merge(
    total_eng_in_disciplined_dis, on='Race/Ethnicity', how='left'
).merge(
    eng_in_disciplined_low, on='Race/Ethnicity', how='left'
).merge(
    total_eng_in_disciplined_low, on='Race/Ethnicity', how='left'
)

# Fill NaN values with 0
merged_df.fillna(0, inplace=True)

# Calculate percentages for each category using the columns in merged_df
merged_df['percentage_disability'] = merged_df['Disabled Total']/merged_df['Total Eligible'] * 100
merged_df['percentage_englearner'] = merged_df['English Learner Total'] / merged_df['Total Eligible'] * 100
merged_df['percentage_lowincome'] = merged_df['Low Income Total'] / merged_df['Total Eligible'] * 100
merged_df['percentage_disability_disciplined'] = merged_df['Disabled Disciplined'] / merged_df['Total Disciplined'] * 100
merged_df['percentage_englearner_disciplined'] = merged_df['English Learner Disciplined'] / merged_df['Total Disciplined'] * 100
merged_df['percentage_lowincome_disciplined'] = merged_df['Low Income Disciplined'] / merged_df['Total Disciplined'] * 100

merged_df['percentage_lowincome_in_total_disabled'] = merged_df['Low Income in Total disabled'] / merged_df['Disabled Total'] * 100
merged_df['percentage_lowincome_in_disciplined_disabled'] = merged_df['Low Income in Disciplined disabled'] / merged_df['Disabled Disciplined'] * 100
merged_df['percentage_disabled_in_total_lowincome'] = merged_df['Low Income in Total disabled'] / merged_df['Low Income Total'] * 100
merged_df['percentage_disabled_in_disciplined_lowincome'] = merged_df['Low Income in Disciplined disabled'] / merged_df['Low Income Disciplined'] * 100

merged_df['percentage_englearner_in_total_disabled'] = merged_df['English in Total disabled'] / merged_df['Disabled Total'] * 100
merged_df['percentage_englearner_in_disciplined_disabled'] = merged_df['English Learner in Disciplined disabled'] / merged_df['Disabled Disciplined'] * 100
merged_df['percentage_disabled_in_total_englearner'] = merged_df['English in Total disabled'] / merged_df['English Learner Total'] * 100
merged_df['percentage_disabled_in_disciplined_englearner'] = merged_df['English Learner in Disciplined disabled'] / merged_df['English Learner Disciplined'] * 100

merged_df['percentage_lowincome_in_total_englearner'] = merged_df['Low Income in total English Learner'] / merged_df['English Learner Total'] * 100
merged_df['percentage_lowincome_in_disciplined_englearner'] = merged_df['Low Income in English learner'] / merged_df['English Learner Disciplined'] * 100
merged_df['percentage_englearner_in_total_lowincome'] = merged_df['Low Income in total English Learner'] / merged_df['Low Income Total'] * 100
merged_df['percentage_englearner_in_disciplined_lowincome'] = merged_df['Low Income in English learner'] / merged_df['Low Income Disciplined'] * 100

# Select only the percentage columns for your final dataframe
final_columns1 = ['Race/Ethnicity', 'percentage_disability', 'percentage_englearner', 'percentage_lowincome', 'percentage_disability_disciplined' ,'percentage_englearner_disciplined','percentage_lowincome_disciplined'] # Include all percentage column names
final_df1 = merged_df[final_columns1]
final_df1=final_df1.set_index('Race/Ethnicity')

final_columns2 = ['Race/Ethnicity', 'percentage_lowincome_in_total_disabled', 'percentage_lowincome_in_disciplined_disabled','percentage_disabled_in_total_lowincome',
'percentage_disabled_in_disciplined_lowincome','percentage_englearner_in_total_disabled','percentage_englearner_in_disciplined_disabled','percentage_disabled_in_total_englearner',
'percentage_disabled_in_disciplined_englearner','percentage_lowincome_in_total_englearner','percentage_lowincome_in_disciplined_englearner','percentage_englearner_in_total_lowincome','percentage_englearner_in_disciplined_lowincome']
final_df2 = merged_df[final_columns2]
final_df2=final_df2.set_index('Race/Ethnicity')


# Rename columns if needed
final_df1.columns = ['% Disability', '% English Learner', '% Low Income', '% Disability in Disciplined', '% English Learners in disciplined', '% Low income in disciplined'] # Include all new column names
final_df2.columns = ['% Low income students in disabled group','% Low income in discplined disabled group', '% disabled in low income', '% disabled in disciplined low income','% english learner in disabled','% english learner in disciplined disabled','% disabled in english learner','% disabled in disciplined english learner', '% lowincome in english learner','% low income in disciplined english learner','% english learner in low income','% english learner in disciplined low income' ]

# preprocess df to make it suitable for upset plot
races = df['Race/Ethnicity'].dropna().unique()
selected_race = st.selectbox("Select the Race for intersectional analysis", races)
df_upset = df.copy()
df_upset = df_upset[(df_upset['Race/Ethnicity'] == selected_race) & (df_upset['Gender'].isnull())]
df_upset['Students w/ Disabilities'] = df_upset['Students w/ Disabilities'].apply(lambda x: True if x == 'With Disability' else False)
df_upset['English Learners'] = df_upset['English Learners'].apply(lambda x: True if x == 'English Learner' else False)
df_upset['Low Income'] = df_upset['Low Income'].apply(lambda x: True if x == 'Low Income' else False)
df_upset['Disciplinary Rate'] = df_upset['Total Disciplined'] / df_upset['Total Eligible'] * 100

columns = ['Students w/ Disabilities', 'English Learners', 'Low Income', 'Disciplinary Rate', 'Total Eligible']
df_upset = df_upset[columns]
df_upset = df_upset.set_index(['Students w/ Disabilities', 'English Learners', 'Low Income'])

from upsetplot import UpSet
import matplotlib.pyplot as plt
# create subplot without axis ticks
fig, ax = plt.subplots()
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
upset = UpSet(df_upset, subset_size='sum', sum_over = 'Total Eligible', intersection_plot_elements=2, orientation='vertical')
upset.add_catplot(value='Disciplinary Rate', kind='bar', color='green')
upset.plot(fig=fig)
fig.set_figwidth(12)
fig.set_figheight(12)
st.pyplot(fig)
st.write("First data")
st.write("Second data")
st.write(final_df2)

