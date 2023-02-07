import numpy as np
import pandas as pd
import re

# extract important features from weather data and apply
def add_weather_info(df: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    weather = weather.drop(columns=[
        'name', 
        'tempmax', 
        'tempmin', 
        'feelslikemax', 
        'feelslikemin', 
        'feelslike', 
        'dew', 
        'humidity', 
        'solarenergy', 
        'uvindex', 
        'severerisk', 
        'sunrise',
        'precip',
        'precipprob',
        'precipcover',
        'snow',
        'snowdepth',
        'windgust',
        'winddir',
        'sealevelpressure',
        'visibility',
        'cloudcover',
        'solarradiation',
        'moonphase',
        'sunset',
        'preciptype',
        'description',
        'icon',
        'stations',
        'windspeed',
    ])

    # regex match Rain, Snow
    snow = re.compile('Snow')
    rain = re.compile('Rain')
    cloudy = re.compile('cloudy|Overcast')
    clear = re.compile('Clear|Sunny')

    weather['conditions'] = weather['conditions'].apply(lambda x: "clear" if re.search(clear, x) else x)
    weather['conditions'] = weather['conditions'].apply(lambda x: "snow" if re.search(snow, x) else x)
    weather['conditions'] = weather['conditions'].apply(lambda x: "rain" if re.search(rain, x) else x)
    weather['conditions'] = weather['conditions'].apply(lambda x: "cloudy" if re.search(cloudy, x) else x)
    weather['conditions'] = weather['conditions'].map({'clear': 0, 'cloudy': 1, 'rain': 2, 'snow': 3})

    weather['datetime'] = pd.to_datetime(weather['datetime'], format='%Y-%m-%d')
    # rename date to Date
    weather = weather.rename(columns={'datetime': 'Date'})
    df = df.merge(weather, on='Date', how='left')

    return df