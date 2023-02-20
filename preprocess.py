from sales_processing import *
from holiday_processing import *
import pandas as pd
"""
Preprocesses the data
Args:
    df: the dataframe to preprocess
    fill_dates: whether to fill in missing dates
    norm_by: [month, year, any] whether to normalize the sales, and if so, by what
    drop_cols: columns to drop
    categorical_features: categorical features to one-hot encode
Returns:
    the preprocessed dataframe
"""
def preprocess(df: pd.DataFrame, fill_dates=True, norm_by=None, drop_cols=None, categorical_features=None) -> pd.DataFrame:
    norms = None
    if fill_dates:
        df = fill_in_dates(df)
    df = add_date_features(df)
    if norm_by is not None:
        match norm_by:
            case 'month':
                df, norms = normalize_sales_month(df)
            case 'year':
                df = normalize_sales_year(df)
            case _:
                df, norms = normalize_sales(df)
    df = add_holidays(df, pd.read_csv('data/swedish_holidays.csv'))
    df = kung_i_baren(df)
    df = find_closed_patterns(df)
    df = find_closed_ranges(df)
    if drop_cols is not None:
        df = df.drop(columns=drop_cols)
    if categorical_features is not None:
        df = one_hot_encode_categorical(df, categorical_features)
    if norms is not None:
        return df, norms
    return df
