import pandas as pd
import streamlit as st
import altair as alt

# Read in the data
df = pd.read_csv("master.csv")

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Filter the dataframe
df = df[(df['District Name'] == district) & (df['School Name'] == district)]

# Create a list of years
years = df['year'].unique()

# Create a list of all race/ethnicity categories
races = ['White', 'African American/Black', 'Hispanic or Latino', 'Asian', 'Multi-race, non-Hispanic or Latino', 'American Indian or Alaskan Native',
       'Native Hawaiian or Pacific Islander']
mapped_colors = ['#FFD966', '#9DC3E6', '#C5E0B4', '#ED7D31', '#7030A0', '#8c564b', '#002060']

# get dynamic column for selectbox
categories = ['All', 'Students w/ Disabilities', 'English Learners', 'Low Income']
cat_values = ['all', 'With Disability', 'English Learner', 'Low Income']

filter_cols = categories[1:]

# Create tabs for each category 
tabs = st.tabs(categories)

def get_filtered_counts(group, filter_cols, attr):
    try:
        value = group.loc[group[filter_cols + ['Gender']].isnull().all(axis=1), attr]
        if value.empty:
            value = group.loc[group[filter_cols].isnull().all(axis=1), :]
            # gender value for male
            male_value = value.loc[value['Gender'] == 'Male', :]
            if male_value.empty:
                male_value = 0
            else:
                male_value = male_value[attr].values[0]
            female_value = value.loc[value['Gender'] == 'Female', :]
            if female_value.empty:
                female_value = 0
            else:
                female_value = female_value[attr].values[0]
            res = male_value + female_value
        else:
            res = value.values[0]
        return res
    except Exception as e:
        print(e)

for tab, cat, cat_val in zip(tabs, categories, cat_values):
    with tab:
        if cat_val == 'all':
            df_filtered = df
            categories_to_check = filter_cols
        else:
            categories_to_check = [col for col in filter_cols if col != cat]
            df_filtered = df[df[cat]== cat_val]
        disciplinary_rate = df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined'))/df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible')) * 100
        disciplinary_rate = disciplinary_rate.reset_index(name='Disciplinary Rate')
        print(disciplinary_rate)

        disciplinary_rate['year'] = disciplinary_rate['year'].astype(str)
        print(disciplinary_rate.head())
        # Create a bar chart for all races across years
        chart = alt.Chart(disciplinary_rate).mark_bar().encode(
            x=alt.X('Race/Ethnicity:O', axis=None),
            y='Disciplinary Rate',
            color=alt.Color(
                'Race/Ethnicity:N',
                scale=alt.Scale(
                    range = mapped_colors,
                    domain = races
                )
            ),
            column='year:N'
        )

        st.write(chart)

