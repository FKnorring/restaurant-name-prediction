import numpy as np
import pandas as pd
from typing import Tuple, Dict
from sklearn.preprocessing import normalize

# normalize sales per company
def normalize_sales(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, float]]:
    norms = {}
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        company_sales = company_df['Sales'].values.reshape(-1, 1)
        normed, norm = normalize(
            company_sales, axis=0, norm='l2', return_norm=True)
        df.loc[company_df.index, 'Sales'] = normed.flatten()
        norms[company] = norm[0]
    return df, norms


def denormalize_sales(df: pd.DataFrame, norms: Dict[int, float]) -> pd.DataFrame:
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        company_df.loc[:, 'Sales'] = company_df['Sales'] * norms[company]
        df[df['Company'] == company] = company_df
    return df
        
# fill in missing dates with 0 sales
def fill_in_dates(df: pd.DataFrame, dates: pd.date_range) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df['Date'])
    index = pd.MultiIndex.from_product(
        [dates, df['Company'].unique()], names=['Date', 'Company'])
    pivot = df.set_index(['Date', 'Company']).reindex(
        index, fill_value=0).reset_index()
    return pivot.sort_values(by=['Date', 'Company'])

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




  