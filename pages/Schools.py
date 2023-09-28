import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

# Read in the data
df = pd.read_csv("master.csv")

districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# select a year
year = st.sidebar.selectbox('Select a year', df['year'].unique())
df = df.loc[df['year'] == year, :]

# Filter the dataframe
df = df[(df['District Name'] == district)]

cats = ['Students w/ Disabilities', 'English Learners', 'Low Income']

# filter for all cats being null
df = df.loc[df[cats].isnull().all(axis=1), :]

df = df.groupby('School Name').agg({'Total Disciplined': 'sum',
                                    'Total Eligible': 'sum'}).reset_index()

print(df.head())

# group by school name and get disciplinary rate
df['Discipline Rate'] = df['Total Disciplined'] / df['Total Eligible']
# create horizontal bar chart with disciplinary rate for each school sorted descending
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Discipline Rate', axis=alt.Axis(format='%')),
    y=alt.Y('School Name', sort='-x')
).properties(
    width=800,
    height=600
)

st.write(chart)
