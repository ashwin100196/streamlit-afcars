import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
from utils import get_filtered_counts, mapped_colors, races

# Read in the data
df = pd.read_csv("master.csv")

# Exclude rows where 'Race/Ethnicity' is null
df = df[df['Race/Ethnicity'].notnull()]

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Filter the dataframe
df = df[(df['District Name'] == district)]

df['year'] = df['year'].apply(lambda y: str(y-1) + '-' + str(y)[2:])

# Create a list of years
years = df['year'].unique()

# Sidebar widget to select years - applies to all categories
years_selected = st.sidebar.multiselect('Select years', years, default=years, key='year_select')
df_filtered_years = df[df['year'].isin(years_selected)]

# Define the order of races and corresponding colors
ordered_races = [
    'White', 'African American/Black', 'Hispanic or Latino', 
    'Asian', 'Multi-race, non-Hispanic or Latino', 
    'American Indian or Alaskan Native', 'Native Hawaiian or Pacific Islander'
]

# Corresponding colors for each race
custom_colors = [
    'yellow', 'lightblue', 'green', 
    'orange', 'purple', 
    'brown', 'darkblue'
]

# Relative Rate Index (RRI) Calculation
# Assuming 'White' is the reference group for RRI
reference_group_rate = df[df['Race/Ethnicity'] == 'White']['Total Disciplined'].sum() / df[df['Race/Ethnicity'] == 'White']['Total Eligible'].sum()

if not np.isnan(reference_group_rate) and reference_group_rate != 0:
    # Get dynamic column for selectbox
    categories = ['All', 'Students w/ Disabilities', 'English Learners', 'Low Income']
    cat_values = ['all', 'With Disability', 'English Learner', 'Low Income']

    # Create tabs for each category
    tabs = st.tabs(categories)

    for tab, cat, cat_val in zip(tabs, categories, cat_values):
        with tab:
            # Filter data based on the category
            if cat_val == 'all':
                df_filtered = df_filtered_years
            else:
                df_filtered = df_filtered_years[df_filtered_years[cat] == cat_val]

            # Calculate RRI for each category
            df_filtered['RRI'] = df_filtered.apply(lambda x: (x['Total Disciplined'] / x['Total Eligible']) / reference_group_rate if x['Race/Ethnicity'] != 'White' and x['Race/Ethnicity'] not in [np.nan, ''] and pd.notnull(x['Total Eligible']) else np.nan, axis=1)
            df_filtered.loc[df_filtered['Race/Ethnicity'] == 'White', 'RRI'] = 1

            # Visualization of RRI for each category
            rri_chart = alt.Chart(df_filtered).mark_bar().encode(
            x=alt.X('Race/Ethnicity', sort=ordered_races),  # Sort the x-axis based on the ordered races
            y='average(RRI)',
            color=alt.Color('Race/Ethnicity', scale=alt.Scale(domain=ordered_races, range=custom_colors))  # Custom color mapping
            ).properties(
            title=f'Relative Rate Index (RRI) of Disciplinary Actions by Race/Ethnicity for {cat}'
            )

            st.altair_chart(rri_chart, use_container_width=True)
