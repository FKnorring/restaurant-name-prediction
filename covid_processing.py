import pandas as pd

def add_covid_info(df: pd.DataFrame, covid: pd.DataFrame) -> pd.DataFrame:

    covid['Statistikdatum'] = pd.to_datetime(covid['Statistikdatum'])

    covid = pd.concat([covid, pd.DataFrame({'Statistikdatum': pd.date_range("2020-01-01","2020-02-03")})], ignore_index=True)
    covid = covid.sort_values(by=['Statistikdatum'])

    #remove dates after 2023-01-04

    covid = covid[covid['Statistikdatum'] < '2023-01-04']
    covid = covid[['Statistikdatum', 'Totalt_antal_fall', 'Uppsala']]
    covid = covid.rename(columns={'Statistikdatum': 'Date'})
    df = df.merge(covid, on='Date', how='left').fillna(0)
    return df
