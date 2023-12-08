import pandas as pd
import streamlit as st
import numpy as np
from scipy.stats import chi2_contingency

# Read in the data
df = pd.read_csv("master.csv")

# Select District
districts = df['District Name'].unique()
district = st.sidebar.selectbox('Select a district', districts)

# Filter the dataframe by selected district
df = df[df['District Name'] == district]

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

# Function to calculate disciplinary rate
def calculate_disciplinary_rate(dataframe):
    return dataframe['Total Disciplined'].sum() / dataframe['Total Eligible'].sum() * 100

# Calculate disciplinary rates for each category
all_students_rate = calculate_disciplinary_rate(df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'].isnull())])

disabled_students_rate = calculate_disciplinary_rate(df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender'].isnull())])

english_learners_rate = calculate_disciplinary_rate(df[(df['English Learners'] == 'English Learner') & (df['Students w/ Disabilities'].isnull()) & (df['Low Income'].isnull()) & (df['Gender'].isnull())])

low_income_students_rate = calculate_disciplinary_rate(df[(df['Low Income'] == 'Low Income') & (df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Gender'].isnull())])

# Display the results
st.write(f"Disciplinary Rate for All Students: {all_students_rate}%")
st.write(f"Disciplinary Rate for Students with Disabilities: {disabled_students_rate}%")
st.write(f"Disciplinary Rate for English Learners: {english_learners_rate}%")
st.write(f"Disciplinary Rate for Low Income Students: {low_income_students_rate}%")

# Function to calculate disciplined counts
def calculate_disciplined(dataframe):
    return dataframe['Total Disciplined'].sum() 

# Function to calculate eligible counts
def calculate_eligible(dataframe):
    return dataframe['Total Eligible'].sum() 

# Calculate disciplined counts for each category
disabled_students_disciplined_count = calculate_disciplined(df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender'].isnull())])

english_learners_disciplined_count = calculate_disciplined(df[(df['English Learners'] == 'English Learner') & (df['Students w/ Disabilities'].isnull()) & (df['Low Income'].isnull()) & (df['Gender'].isnull())])

low_income_students_disciplined_count = calculate_disciplined(df[(df['Low Income'] == 'Low Income') & (df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Gender'].isnull())])

# Calculate eligible counts for each category
disabled_students_eligible_count = calculate_eligible(df[(df['Students w/ Disabilities'] == 'With Disability') & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender'].isnull())])

english_learners_eligible_count = calculate_eligible(df[(df['English Learners'] == 'English Learner') & (df['Students w/ Disabilities'].isnull()) & (df['Low Income'].isnull()) & (df['Gender'].isnull())])

low_income_students_eligible_count = calculate_eligible(df[(df['Low Income'] == 'Low Income') & (df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Gender'].isnull())])

# Calculate not disciplined counts for each category

disabled_students_notdisciplined_count = disabled_students_eligible_count - disabled_students_disciplined_count
english_learners_notdisciplined_count = english_learners_eligible_count - english_learners_disciplined_count
low_income_students_notdisciplined_count = low_income_students_eligible_count - low_income_students_disciplined_count

# Create the contingency table
contingency_table = np.array([
    [disabled_students_disciplined_count, disabled_students_notdisciplined_count],
    [english_learners_disciplined_count, english_learners_notdisciplined_count],
    [low_income_students_disciplined_count, low_income_students_notdisciplined_count]
])

# Convert the contingency table to a pandas DataFrame for display
contingency_df = pd.DataFrame(
    contingency_table, 
    columns=['Disciplined', 'Not Disciplined'], 
    index=['Students w/ Disabilities', 'English Learners', 'Low Income']
)

# Display the contingency table
st.write("Contingency Table:")
st.write(contingency_df)

# Perform the Chi-square test
chi2_stat, p_val, dof, expected = chi2_contingency(contingency_table)

# Display the results
st.write("Chi-square Statistic:", chi2_stat)
st.write("P-value:", p_val)

# Interpretation of results
if p_val < 0.05:
    st.write("There is a statistically significant difference in disciplinary actions across categories.")
else:
    st.write("There is no statistically significant difference in disciplinary actions across categories.")

st.write("Gender Based Analysis")

# Calculate disciplined counts for each gender 
male_students_disciplined_count = calculate_disciplined(df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender']== 'Male')])

Female_students_disciplined_count = calculate_disciplined(df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender']== 'Female')])


# Calculate eligible counts for each category
male_students_eligible_count = calculate_eligible(df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender']== 'Male')])

Female_students_eligible_count = calculate_eligible(df[(df['Students w/ Disabilities'].isnull()) & (df['English Learners'].isnull()) & (df['Low Income'].isnull()) & (df['Gender']== 'Female')])


# Calculate not disciplined counts for each category

male_students_notdisciplined_count = male_students_eligible_count - male_students_disciplined_count
Female_students_notdisciplined_count = Female_students_eligible_count - Female_students_disciplined_count

# Create a contingency table for gender
contingency_gender = np.array([[male_students_disciplined_count, male_students_notdisciplined_count],
                               [Female_students_disciplined_count, Female_students_notdisciplined_count]])

# Convert the contingency table to a pandas DataFrame for display
contingency_gender_df = pd.DataFrame(
    contingency_gender, 
    columns=['Disciplined', 'Not Disciplined'], 
    index=['Male', 'Female']
)

# Display the contingency table
st.write("Contingency Table for Gender analysis:")
st.write(contingency_gender_df)

# Perform Chi-square test
chi2_gender, p_gender = chi2_contingency(contingency_gender)[:2]

# Display the results
st.write("Gender-Based Disciplinary Actions Analysis:")
st.write("Chi-square statistic:", chi2_gender)
st.write("P-value:", p_gender)

# Interpretation of results
if p_val < 0.05:
    st.write("There is a statistically significant difference in disciplinary actions across gender categories.")
else:
    st.write("There is no statistically significant difference in disciplinary actions across gender categories.")