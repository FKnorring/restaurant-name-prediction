import numpy as np
import pandas as pd

# Add holidays to dataframe
def add_holidays(df: pd.DataFrame, holidays: pd.DataFrame) -> pd.DataFrame:
    df['Holiday'] = df['Date'].isin(
        holidays[holidays['Day'].str.contains("Day")]['Date']).astype(int)
    df['Holieve'] = df['Date'].isin(
        holidays[holidays['Day'].str.contains("Eve")]['Date']).astype(int)
    return df
