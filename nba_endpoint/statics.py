import os
import pandas as pd 

def retrieve_leaguedashplayerbiostats():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)
    os.chdir('../data')
    
    output = pd.read_pickle("nba_playerbiostats.pkl")
    seasons = output.SEASON.unique()
    print(f"Data retrieved from {min(seasons)} to {max(seasons)}")
    return output
    