import pandas as pd
import streamlit as st
import altair as alt
from geopy.geocoders import GoogleV3
import folium
import numpy as np
from utils import get_filtered_counts, mapped_colors, races
import geopandas as gpd 

# Load the Shapefile
gdf = gpd.read_file('TOWNSSURVEY_POLY.shp')

# Specify the geometry column
geometry_column = "geometry"  

# Create a GeoDataFrame with latitude and longitude columns
# Here, we calculate the centroid of each polygon to get the approximate latitude and longitude
gdf['latitude'] = gdf.centroid.y
gdf['longitude'] = gdf.centroid.x

# Create a Streamlit map using Folium
st.subheader("Map")

# Display the map using st.map() with latitude and longitude columns
st.map(gdf[['latitude', 'longitude']], zoom=5, tile_provider="Stamen Terrain")


# Add a sidebar for user interaction
# selected_district = st.sidebar.selectbox('Select a District:', gdf['TOWN'].unique())
# selected_district_geo = gdf[gdf['TOWN'] == selected_district]


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

# get dynamic column for selectbox
categories = ['All', 'Students w/ Disabilities', 'English Learners', 'Low Income']
cat_values = ['all', 'With Disability', 'English Learner', 'Low Income']

filter_cols = categories[1:]

# Create tabs for each category 
tabs = st.tabs(categories)

years_selected = st.sidebar.multiselect('Select years', years, default=years, key='year_select')
df_filtered_years = df[df['year'].isin(years_selected)]

for tab, cat, cat_val in zip(tabs, categories, cat_values):
    with tab:
        if cat_val == 'all':
            df_filtered = df_filtered_years
            categories_to_check = filter_cols
        else:
            categories_to_check = [col for col in filter_cols if col != cat]
            df_non_filtered = df_filtered_years.copy()
            df_non_filtered = df_non_filtered[df_non_filtered[cat].isnull()]
            df_filtered = df_filtered_years[df_filtered_years[cat]== cat_val]
        try:
            num = df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined'))
            denom = df_filtered.groupby(['Race/Ethnicity', 'year']).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible'))
            disciplinary_rate = num/denom * 100
            disciplinary_rate = disciplinary_rate.reset_index(name='Disciplinary Rate')
        except:
            import pdb; pdb.set_trace()

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

        # TODO: check cambridge data not showing red bars for 2020
        # TODO: create avg rate of disciplinary action
        # TODO: breakdown impact of low income with % disability

        if cat_val != 'all':
            st.write("Impact of discipline on " + cat_val + " students in " + district + " district")
            for year in df_filtered['year'].unique():
                st.header(year)
                df_year_filtered = df_filtered[df_filtered['year'] == year]
                df_year_non_filtered = df_non_filtered[df_non_filtered['year'] == year]
                # get percentage of category students disciplined
                group_key = ['Race/Ethnicity']
                category_disciplined_percentage = df_year_filtered.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined'))/df_year_non_filtered.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Disciplined', mode='sum')) * 100
                category_disciplined_percentage = category_disciplined_percentage.reset_index(name='percentage_cat')
                category_disciplined_percentage['sample'] = 'Disciplined'

                # get percentage of category students in population
                category_students_percentage = df_year_filtered.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible'))/df_year_non_filtered.groupby(group_key).apply(lambda grp: get_filtered_counts(grp, categories_to_check, 'Total Eligible', mode='sum')) * 100
                category_students_percentage = category_students_percentage.reset_index(name='percentage_cat')
                category_students_percentage['sample'] = 'Population'

                # concatenate the two dataframes
                concat_df = pd.concat([category_disciplined_percentage, category_students_percentage], axis=0)

                bar = alt.Chart(concat_df).mark_bar().encode(
                    color=alt.Color(
                            'Race/Ethnicity:N',
                        scale=alt.Scale(
                            range = mapped_colors,
                            domain = races
                        )
                    ),
                    x='Race/Ethnicity',
                    y='percentage_cat',
                    column='sample:N'
                ).properties(
                    width=alt.Step(40)  # controls width of bar.
                )

                st.write(bar)
    
                 
                