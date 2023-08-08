import pandas as pd
import streamlit as st
import altair as alt

# Read in the data
df = pd.read_csv("master.csv")

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Filter the dataframe
df = df[(df['District Name'] == district) & (df['School Name'] == district)]

df['year'] = df['year'].apply(lambda y: str(y-1) + '-' + str(y)[2:])

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

def get_filtered_counts(group, filter_cols, attr, mode='one'):
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
        elif mode == 'one':
            res = value.values[0]
        elif mode == 'sum':
            res = value.sum()
        else:
            raise AttributeError('Invalid mode')
        return res
    except Exception as e:
        print(e)

years_selected = st.sidebar.multiselect('Select years', years, default=years, key='year_select')
df_filtered_years = df[df['year'].isin(years_selected)]

for tab, cat, cat_val in zip(tabs, categories, cat_values):
    with tab:
        if cat_val == 'all':
            df_filtered = df_filtered_years
            categories_to_check = filter_cols
        else:
            categories_to_check = [col for col in filter_cols if col != cat]
            df_filtered = df_filtered_years[df_filtered_years[cat]== cat_val]
        disciplinary_rate = df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined'))/df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible')) * 100
        disciplinary_rate = disciplinary_rate.reset_index(name='Disciplinary Rate')

        disciplinary_rate['year'] = disciplinary_rate['year'].astype(str)
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

        st.write("Race breakdown for " + cat_val + " students in " + district + " district")

        race_disciplined_counts = df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined')).reset_index(name='disciplined_counts')

        total_disciplined_counts = df_filtered.groupby(['year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined', mode='sum')).reset_index(name='total_disciplined_counts')

        # merge the two dataframes on year
        merged_df = pd.merge(race_disciplined_counts, total_disciplined_counts, on='year')
        merged_df['percentage disciplined'] = merged_df['disciplined_counts']/merged_df['total_disciplined_counts'] * 100

        race_counts = df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible')).reset_index(name='eligible_counts')
        total_counts = df_filtered.groupby(['year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible', mode='sum')).reset_index(name='total_counts')

        # merge the two dataframes on year
        population_df = pd.merge(race_counts, total_counts, on='year')
        population_df['percentage total'] = population_df['eligible_counts']/population_df['total_counts'] * 100

        race_breakdown = pd.concat([merged_df, population_df.drop(columns=['Race/Ethnicity', 'year'])], axis=1)
        bar = alt.Chart(race_breakdown).mark_bar().encode(
            color=alt.Color(
                    'Race/Ethnicity:N',
                scale=alt.Scale(
                    range = mapped_colors,
                    domain = races
                )
            ),
            x='Race/Ethnicity',
            y='percentage total'
        ).properties(
            width=alt.Step(40)  # controls width of bar.
        )

        tick = alt.Chart(race_breakdown).mark_tick(
            color='red',
            thickness=4,
            size=40,  # controls width of tick.
        ).encode(
            x='Race/Ethnicity',
            y='percentage disciplined'
        )

        chart2 = alt.layer(bar, tick).facet(column='year:N')

        st.write(chart2)
