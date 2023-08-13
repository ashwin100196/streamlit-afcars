import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
from utils import get_filtered_counts, mapped_colors, races

# Read in the data
df = pd.read_csv("master.csv")

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Filter the dataframe
df = df[(df['District Name'] == district) & (df['School Name'] == district)]

df['year'] = df['year'].apply(lambda y: str(y-1) + '-' + str(y)[2:])

# Create a list of years
years = df['year'].unique()
year = st.sidebar.selectbox('Select a year', years)

# Filter the dataframe
df = df[df['year'] == year]

# for year in years:
df_dis_total = df[df['Students w/ Disabilities'].isnull() & df['English Learners'].isnull() & df['Low Income'].isnull()]
disciplined_total = df_dis_total.groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Total Disciplined')
total_eligible = df_dis_total.groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Total Eligible')

df_dis = df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'].isnull())]
disciplined_disabled = df_dis.loc[df_dis['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Disabled Disciplined')
total_disabled = df_dis.loc[df_dis['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Disabled Total')

df_low = df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'] == 'Low Income')]
disciplined_low = df_low.loc[df_low['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Disciplined'].sum().reset_index(name='Low Income Disciplined')
total_low = df_low.loc[df_low['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Low Income Total')

df_low_pop = df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'] == 'Low Income')]
total_low_pop = df_low_pop.loc[df_low_pop['Gender'].isnull(), :].groupby('Race/Ethnicity')['Total Eligible'].sum().reset_index(name='Low Income Total Population')

# merge dataframes on Race/Ethnicity
final_df = disciplined_total.merge(total_eligible, on='Race/Ethnicity', how='left').merge(disciplined_disabled, on='Race/Ethnicity', how='left').merge(total_disabled, on='Race/Ethnicity', how='left').merge(disciplined_low, on='Race/Ethnicity', how='left').merge(total_low, on='Race/Ethnicity', how='left')

percentage_disability = total_disabled.set_index('Race/Ethnicity')['Disabled Total']/total_eligible.set_index('Race/Ethnicity')['Total Eligible'] * 100
percentage_disability_disciplined = disciplined_disabled.set_index('Race/Ethnicity')['Disabled Disciplined']/disciplined_total.set_index('Race/Ethnicity')['Total Disciplined'] * 100
percentage_low = disciplined_low.set_index('Race/Ethnicity')['Low Income Disciplined']/disciplined_disabled.set_index('Race/Ethnicity')['Disabled Disciplined'] * 100
percentage_low_pop = total_low_pop.set_index('Race/Ethnicity')['Low Income Total Population']/total_eligible.set_index('Race/Ethnicity')['Total Eligible'] * 100

# concatenate dataframes
res_df = pd.concat([percentage_disability, percentage_disability_disciplined, percentage_low, percentage_low_pop], axis=1)
# rename columns
res_df.columns = ['% disability', '% disability in disciplined', '% Low Income in disabled', '% Low Income Population']

st.write(res_df)

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

