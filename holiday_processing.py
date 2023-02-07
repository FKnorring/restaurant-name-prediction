import numpy as np
import pandas as pd

# Add holidays to dataframe
def add_holidays(df: pd.DataFrame, holidays: pd.DataFrame) -> pd.DataFrame:
    df['Holiday'] = df['Date'].isin(holidays['Date']).astype(int)
    return df