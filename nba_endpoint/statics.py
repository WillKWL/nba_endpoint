import os
import pandas as pd 

def retrieve_leaguedashplayerbiostats(columns = None):    
    """retrieve latest player bio data to avoid multiple requests

    Returns:
        df: pandas dataframe of data
    """
    output = pd.read_pickle("https://github.com/WillKWL/nba_endpoint/blob/master/data/nba_playerbiostats.pkl?raw=true")
    if columns is not None:
        output = output[columns]
    seasons = output.SEASON.unique()
    print(f"Data retrieved from {min(seasons)} to {max(seasons)}")
    return output


if __name__ == '__main__':
    data = retrieve_leaguedashplayerbiostats()
    print(data.head())