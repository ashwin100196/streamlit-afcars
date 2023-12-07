import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
from utils import get_filtered_counts, mapped_colors, races

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

final_columns2 = ['percentage_lowincome_in_total_disabled', 'percentage_lowincome_in_disciplined_disabled','percentage_disabled_in_total_lowincome',
'percentage_disabled_in_disciplined_lowincome','percentage_englearner_in_total_disabled','percentage_englearner_in_disciplined_disabled','percentage_disabled_in_total_englearner',
'percentage_disabled_in_disciplined_englearner','percentage_lowincome_in_total_englearner','percentage_lowincome_in_disciplined_englearner','percentage_englearner_in_total_lowincome','percentage_englearner_in_disciplined_lowincome']
final_df2 = merged_df[final_columns2]


# Rename columns if needed
final_df1.columns = ['% Disability', '% English Learner', '% Low Income', '% Disability in Disciplined', '% English Learners in disciplined', '% Low income in disciplined'] # Include all new column names
final_df2.columns = ['% Low income students in disabled group','% Low income in discplined disabled group', '% disabled in low income', '% disabled in disciplined low income','% english learner in disabled','% english learner in disciplined disabled','% disabled in english learner','% disabled in disciplined english learner', '% lowincome in english learner','% low income in disciplined english learner','% english learner in low income','% english learner in disciplined low income' ]

# Use Streamlit to display the dataframe
st.write("First data")
st.write(final_df1)
st.write("Second data")
st.write(final_df2)
st.write(merged_df)





# merge dataframes on Race/Ethnicity
#final_df = disciplined_total.merge(total_eligible, on='Race/Ethnicity', how='left').merge(disciplined_disabled, on='Race/Ethnicity', how='left').merge(total_disabled, on='Race/Ethnicity', how='left').merge(disciplined_low, on='Race/Ethnicity', how='left').merge(total_low, on='Race/Ethnicity', how='left')

#percentage_disability = total_disabled.set_index('Race/Ethnicity')['Disabled Total']/total_eligible.set_index('Race/Ethnicity')['Total Eligible'] * 100
#percentage_englearner = total_eng.set_index('Race/Ethnicity')['English Learner Total']/total_eligible.set_index('Race/Ethnicity')['Total Eligible'] * 100
#percentage_lowincome = total_lowinc.set_index('Race/Ethnicity')['Low Income Total']/total_eligible.set_index('Race/Ethnicity')['Total Eligible'] * 100
#percentage_disability_disciplined = disciplined_disabled.set_index('Race/Ethnicity')['Disabled Disciplined']/disciplined_total.set_index('Race/Ethnicity')['Total Disciplined'] * 100
#percentage_englearner_disciplined = disciplined_eng.set_index('Race/Ethnicity')['English Learner Disciplined']/disciplined_total.set_index('Race/Ethnicity')['Total Disciplined'] * 100
#percentage_lowincome_disciplined = disciplined_lowinc.set_index('Race/Ethnicity')['Low Income Disciplined']/disciplined_total.set_index('Race/Ethnicity')['Total Disciplined'] * 100

#percentage_lowincome_in_total_disabled = total_low_in_disciplined_dis.set_index('Race/Ethnicity')['Low Income in Total disabled']/total_disabled.set_index('Race/Ethnicity')['Disabled Total'] * 100
#percentage_lowincome_in_disciplined_disabled = low_in_disciplined_dis.set_index('Race/Ethnicity')['Low Income in Disciplined disabled']/disciplined_disabled.set_index('Race/Ethnicity')['Disabled Disciplined'] * 100
#percentage_disabled_in_total_lowincome = total_low_in_disciplined_dis.set_index('Race/Ethnicity')['Low Income in Total disabled']/total_lowinc.set_index('Race/Ethnicity')['Low Income Total'] * 100
#percentage_disabled_in_disciplined_lowincome = low_in_disciplined_dis.set_index('Race/Ethnicity')['Low Income in Disciplined disabled']/disciplined_lowinc.set_index('Race/Ethnicity')['Low Income Disciplined'] * 100

#percentage_englearner_in_total_disabled = total_eng_in_disciplined_dis.set_index('Race/Ethnicity')['English in Total disabled']/total_disabled.set_index('Race/Ethnicity')['Disabled Total'] * 100
#percentage_englearner_in_disciplined_disabled = low_in_disciplined_dis.set_index('Race/Ethnicity')['English Learner in Disciplined disabled']/disciplined_disabled.set_index('Race/Ethnicity')['Disabled Disciplined'] * 100
#percentage_disabled_in_total_englearner = total_eng_in_disciplined_dis.set_index('Race/Ethnicity')['English in Total disabled']/total_eng.set_index('Race/Ethnicity')['English Learner Total'] * 100
#percentage_disabled_in_disciplined_englearner = low_in_disciplined_dis.set_index('Race/Ethnicity')['English Learner in Disciplined disabled']/disciplined_eng.set_index('Race/Ethnicity')['English Learner Disciplined'] * 100

#percentage_lowincome_in_total_englearner = total_eng_in_disciplined_low.set_index('Race/Ethnicity')['Low Income in total English Learner disabled']/total_eng.set_index('Race/Ethnicity')['English Learner Total'] * 100
#percentage_lowincome_in_disciplined_englearner = low_in_disciplined_dis.set_index('Race/Ethnicity')['Low Income in English learner disabled']/disciplined_eng.set_index('Race/Ethnicity')['English Learner Disciplined'] * 100
#percentage_englearner_in_total_lowincome = total_eng_in_disciplined_low.set_index('Race/Ethnicity')['Low Income in total English Learner disabled']/total_lowinc.set_index('Race/Ethnicity')['Low Income Total'] * 100
#percentage_englearner_in_disciplined_lowincome = low_in_disciplined_dis.set_index('Race/Ethnicity')['Low Income in English learner disabled']/disciplined_lowinc.set_index('Race/Ethnicity')['Low Income Disciplined'] * 100

# concatenate dataframes for 1st round
#res_df = pd.concat([percentage_disability, percentage_disability_disciplined, percentage_englearner, percentage_englearner_disciplined, percentage_lowincome, percentage_lowincome_disciplined], axis=1) #  percentage_disability_disciplined, percentage_low, percentage_low_pop], axis=1)
# rename columns
#res_df.columns = ['% disability', '% disability in disciplined', '% English learner', '% English learner in disciplined', '% Low income', '% Lowincome in disciplined ']

# concatenate dataframes for 2nd round
#res_df1 = pd.concat([percentage_lowincome_in_total_disabled, percentage_lowincome_in_disciplined_disabled, percentage_disabled_in_total_lowincome, percentage_disabled_in_disciplined_lowincome, percentage_englearner_in_total_disabled, percentage_englearner_in_disciplined_disabled, percentage_disabled_in_total_englearner, percentage_disabled_in_disciplined_englearner,percentage_lowincome_in_total_englearner, percentage_lowincome_in_disciplined_englearner, percentage_englearner_in_total_lowincome, percentage_englearner_in_disciplined_lowincome], axis=1) #  percentage_disability_disciplined, percentage_low, percentage_low_pop], axis=1)
# rename columns
#res_df1.columns = ['% lowincome in total disciplined students', '% lowincome in disciplined disabled', '% disabled in total low income', '% disabled in disciplined low income', '% engish learner in total disabled students', '% english learner in diciplined disabled studnets', '% disabled in total english learners', '% disabled in disciplined english learners', '% low income in total english learners', "% low income in disciplined english learners", "% english learner in total low income students", "% englis learner in disciplined low income students"]

#st.write(res_df)
#st.write(res_df1)

# cats = ['Students w/ Disabilities', 'English Learners', 'Low Income']

    # dis_cats = cats[1:]
    # inc_cats = [cats[0], cats[2]]

    # df_dis = df.loc[df['Students w/ Disabilities'] == 'With Disability', :]
    # df_non_filtered = df[df['Students w/ Disabilities'].isnull()]

    # group_key = ['Race/Ethnicity']
    # category_disciplined_percentage = df_dis.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, dis_cats, 'Total Disciplined'))/df_non_filtered.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, dis_cats, 'Total Disciplined', mode='sum')) * 100
    # category_disciplined_percentage = category_disciplined_percentage.reset_index(name='percentage_disability')
    # category_disciplined_percentage['sample'] = 'Disciplined'

    # # get percentage of category students in population
    # category_students_percentage = df_dis.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, dis_cats, 'Total Eligible'))/df_non_filtered.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, dis_cats, 'Total Eligible', mode='sum')) * 100
    # category_students_percentage = category_students_percentage.reset_index(name='percentage_disability')
    # category_students_percentage['sample'] = 'Population'

    # # concatenate the two dataframes
    # concat_df = pd.concat([category_disciplined_percentage, category_students_percentage], axis=0)

    # bar = alt.Chart(concat_df).mark_bar().encode(
    #     color=alt.Color(
    #             'Race/Ethnicity:N',
    #         scale=alt.Scale(
    #             range = mapped_colors,
    #             domain = races
    #         )
    #     ),
    #     x='Race/Ethnicity',
    #     y='percentage_disability',
    #     column='sample:N'
    # ).properties(
    #     width=alt.Step(40)  # controls width of bar.
    # )

    # st.write(bar)

