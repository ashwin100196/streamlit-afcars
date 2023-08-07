import pandas as pd

# Read in the data

years = [2018, 2019, 2020, 2021, 2022]

# Create a list of dataframes
dataframes = []

for year in years:
    filename = 'Discipline ' + str(year) + ' all schools and districts - race - gender - spop.xlsx'
    df = pd.read_excel(filename)
    if year != 2022:
        df.loc[df['Economically Disadvantaged'] == 'Economically Disadvantaged', 'Low Income'] = 'Low Income'
        df.drop('Economically Disadvantaged', axis=1, inplace=True)
    df['year'] = year
    dataframes.append(df)

# Concatenate all dataframes in the list
df = pd.concat(dataframes, axis=0)

# Write the concatenated dataframe to an excel file
df.to_csv("master.csv", index=False)
