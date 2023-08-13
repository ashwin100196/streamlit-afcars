import pandas as pd

# Create a list of all race/ethnicity categories
races = ['White', 'African American/Black', 'Hispanic or Latino', 'Asian', 'Multi-race, non-Hispanic or Latino', 'American Indian or Alaskan Native',
       'Native Hawaiian or Pacific Islander']
mapped_colors = ['#FFD966', '#9DC3E6', '#C5E0B4', '#ED7D31', '#7030A0', '#8c564b', '#002060']

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
            value = pd.Series(male_value + female_value)
        if mode == 'one':
            res = value.values[0]
        elif mode == 'sum':
            res = value.sum()
        else:
            raise AttributeError('Invalid mode')
        return res
    except Exception as e:
        print(e)