import pandas as pd
import numpy as np
from scipy import stats
import streamlit as st

# Load the data
df = pd.read_csv("master.csv")

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Create a dropdown for selecting a school within the district
selected_school = st.sidebar.selectbox('Select a School:', df[df['District Name'] == district]['School Name'].unique())

# Filter the dataframe
df = df[(df['District Name'] == district) & (df['School Name'] == selected_school)]

# Transform 'Year' column and Select Year
df['year'] = df['year'].apply(lambda y: str(y-1) + '-' + str(y)[2:])
years = df['year'].unique()
year = st.sidebar.selectbox('Select a year', years)

# Filter the dataframe by selected year
df = df[df['year'] == year]

# Filter the DataFrame to include only rows where 'Gender' is null
df = df[df['Gender'].isnull()]

# Group the data by 'Race/Ethnicity' and sum up 'Total Disciplined' and 'Total Eligible'
grouped = df.groupby('Race/Ethnicity')[['Total Disciplined', 'Total Eligible']].sum()
grouped['Disciplinary Rate'] = grouped['Total Disciplined'] / grouped['Total Eligible'] * 100

# Prepare the DataFrame for ANOVA test
anova_df = pd.DataFrame()

# List to hold disciplinary rates for each group
disciplinary_rates = []

# Obtain the disciplinary rates for each race and prepare the DataFrame
for race in grouped.index:
    race_df = df[df['Race/Ethnicity'] == race]
    rates = race_df['Total Disciplined'] / race_df['Total Eligible']
    rates_dropna = rates.dropna()  # Drop NaN values
    disciplinary_rates.append(rates_dropna)  # Append the series of rates
    race_df = race_df.assign(Disciplinary_Rate=rates_dropna).dropna(subset=['Disciplinary_Rate'])
    anova_df = pd.concat([anova_df, race_df[['Race/Ethnicity', 'Disciplinary_Rate']]], ignore_index=True)

# Check that we have more than one rate to compare
if len(disciplinary_rates) > 1:
    # Perform ANOVA test only if there are multiple groups to compare
    f_val, p_val = stats.f_oneway(*disciplinary_rates)

    # Display the results
    st.write("ANOVA Test Results for Disciplinary Rates Across Racial/Ethnic Groups:")
    st.write(f"F-value: {f_val}")
    st.write(f"P-value: {p_val}")

    # Interpretation of results
    if p_val < 0.05:
        st.write("There are statistically significant differences in disciplinary rates across racial/ethnic groups.")
    else:
        st.write("There are no statistically significant differences in disciplinary rates across racial/ethnic groups.")
else:
    st.write("Not enough data to perform ANOVA test. Need at least two groups.")

# Display the disciplinary rates
st.write("Disciplinary Rates by Race/Ethnicity:")
st.write(grouped['Disciplinary Rate'])

# Display the table used for the ANOVA test
st.write("Data Used for ANOVA Test:")
st.write(anova_df)
