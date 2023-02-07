import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize

# normalize sales per company
def normalize_sales(df: pd.DataFrame):
    min_max = {}
    for company in [0,1,2]:
        min_max[company] = (df[df['Company'] == company]['Sales'].min(), df[df['Company'] == company]['Sales'].max())

    for company in min_max:
        df['Sales'][df['Company'] == company] = normalize(df['Sales'][df['Company'] == company].values.reshape(1, -1), norm='max', axis=1)
    return df, min_max

def denormalize_sales(df: pd.DataFrame, min_max: dict) -> pd.DataFrame:
    for company in df['Company'].unique():
        df['Sales'][df['Company'] == company] = df['Sales'][df['Company'] == company] * (min_max[company][1] - min_max[company][0]) + min_max[company][0]
    return df
        
# fill in missing dates with 0 sales
def fill_in_dates(df: pd.DataFrame, dates: pd.date_range) -> pd.DataFrame:
    # if there is no date for a certain company in df, add that row with the company to df
    df['Date'] = pd.to_datetime(df['Date'])
    for company in df['Company'].unique():
        fill = pd.DataFrame({'Date': dates, 'Company': company, 'Sales': 0})
        df = pd.concat([df, fill], ignore_index=True)
        df = df.drop_duplicates(subset=['Date', 'Company'], keep='first')
        
    return df.sort_values(by=['Date', 'Company']).reset_index().drop(columns=['index'])

# add day week month year weekday, weekend (friday, saturday) from dates
def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.day
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['Weekday'] = df['Date'].dt.weekday
    df['Weekend'] = df['Date'].dt.weekday.isin([4,5]).astype(int)
    df['Workday'] = df['Date'].dt.weekday.isin([0,1,2,3]).astype(int)
    return df




  