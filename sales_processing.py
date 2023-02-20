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

#normalize sales in chunks
def normalize_sales_chunk(df: pd.DataFrame, chunks: int) -> Tuple[pd.DataFrame, Dict[int, float]]:
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        company_sales = company_df['Sales'].values.reshape(-1, 1)
        chunk_size = len(company_sales) // chunks
        for i in range(0, len(company_sales), chunk_size):
            normed = normalize(company_sales[i:i+chunk_size], axis=0, norm='l2')
            df.loc[company_df.index[i:i+chunk_size], 'Sales'] = normed.flatten()
    return df

# normalize sales per year and month
def normalize_sales_month(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, float]]:
    norms = {}
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        for year in company_df['Year'].unique():
            for month in company_df['Month'].unique():
                
                company_month_df = company_df[(company_df['Year'] == year) & (company_df['Month'] == month)]
                company_month_sales = company_month_df['Sales'].values.reshape(-1, 1)
                if len(company_month_sales) == 0:
                    continue
                if year == 3 and month == 1:
                    # calculate norm from year 2 and month 12 and apply to current
                    _, norm = normalize(company_df[(company_df['Year'] == 2) & (company_df['Month'] == 12)]['Sales'].values.reshape(-1, 1), axis=0, norm='l2', return_norm=True)
                    norms[company] = norm
                    normed = company_month_df['Sales'].values.reshape(-1, 1) / norm
                else:
                    normed = normalize(company_month_sales, axis=0, norm='l2')
                df.loc[company_month_df.index, 'Sales'] = normed.flatten()
    # for last month, normzae with previous month
    return df, norms

#normalize sales per year
def normalize_sales_year(df: pd.DataFrame) -> pd.DataFrame:
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        for year in company_df['Year'].unique():
            company_year_df = company_df[company_df['Year'] == year]
            company_year_sales = company_year_df['Sales'].values.reshape(-1, 1)
            if len(company_year_sales) == 0:
                continue
            normed = normalize(company_year_sales, axis=0, norm='l2')
            df.loc[company_year_df.index, 'Sales'] = normed.flatten()
    return df



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
    df['Year'] = df['Date'].dt.year.map(lambda x: x - 2020)
    df['Weekday'] = df['Date'].dt.weekday
    df['Weekend'] = df['Date'].dt.weekday.isin([4,5]).astype(int)
    df['Workday'] = df['Date'].dt.weekday.isin([0,1,2,3]).astype(int)
    return df

def kung_i_baren(df: pd.DataFrame) -> pd.DataFrame:
    # if a week contains the 25th of the month, it is a special week
    df['Payweek'] = 0
    for i, row in df.iterrows():
        if row['Day'] == 25:
            df.loc[i, 'Payweek'] = 1
        elif (df[(df['Week'] == row['Week']) & (df['Year'] == row['Year']) & (df['Day'] == 25)].empty == False):
            df.loc[i, 'Payweek'] = 1
    # payday are if payweek is 1 and weekday is 4
    df['Payday'] = 0
    df.loc[(df['Payweek'] == 1) & (df['Weekday'] == 4), 'Payday'] = 1
    return df

def add_closed_days(df: pd.DataFrame) -> pd.DataFrame:
    df['Closed'] = df['Sales'].apply(lambda x: 1 if x == 0 else 0)
    return df


# find patterns with day and month where companies have closed
def find_closed_patterns(df: pd.DataFrame, verbose=False) -> pd.DataFrame:
    df['Closed'] = 0
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        for day in company_df['Day'].unique():
            for month in company_df['Month'].unique():
                company_day_month_df = company_df[(company_df['Day'] == day) & (company_df['Month'] == month)]
                #sum days the dataframe['Sales'] == 0
                times_closed = (company_day_month_df['Sales'] == 0).sum()
                if times_closed > 1:
                    if verbose: print(f'Company {company} closed on {day}/{month}, {times_closed} times')
                    # add closed to all days/month in df
                    df.loc[(df['Company'] == company) & (df['Day'] == day) & (df['Month'] == month), 'Closed'] = 1
    return df

# find date ranges where companies have closed
def find_closed_ranges(df: pd.DataFrame, verbose=False) -> pd.DataFrame:
    # print the found ranges
    for company in df['Company'].unique():
        company_df = df[df['Company'] == company]
        # find ranges where sales are 0
        ranges = []
        for i, row in company_df.iterrows():
            if row['Sales'] == 0:
                ranges.append(row['Date'])
            else:
                if len(ranges) > 3:
                    if verbose: print(f'Company {company} closed between {ranges[0]} and {ranges[-1]}')
                    # set closed = 1 for all dates in range
                    df.loc[(df['Company'] == company) & (df['Date'] >= ranges[0]) & (df['Date'] <= ranges[-1]), 'Closed'] = 1
                ranges = []
    return df

def one_hot_encode_categorical(df: pd.DataFrame, categorical_features) -> pd.DataFrame:
    df = pd.get_dummies(df, columns=categorical_features)
    return df
