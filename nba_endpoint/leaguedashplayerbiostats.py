import requests
import pandas as pd
import numpy as np
import time
import os
import pickle

def request_data(start_year, end_year, time_sleep = 0.5):
    """request player bio data from nba.stats

    Args:
        start_year (int): year to start collecting data, e.g. 1996 for 1996-97 season
        end_year (int): year to end collecting data, e.g. 2023 for 2022-23 season
        time_sleep (float, optional): Defaults to sleep for 0.5s between each request.

    Returns:
        df: pandas dataframe of data
    """
    # hard to get numbers of years in nba (cannot determine thru draft year since some players are undrafted, some left the league then returned to NBA)
    # start_year = 1996 
    # end_year = 2023
    # time_sleep = 0.5
    season_list = [str(i) + '-' + str(i+1)[2:] for i in range(start_year, end_year)]

    s = requests.Session()
    output = None
    payload = {
                "College": "",
                "Conference": "",
                "Country": "",
                "DateFrom": "",
                "DateTo": "",
                "Division": "",
                "DraftPick": "",
                "DraftYear": "",
                "GameScope": "",
                "GameSegment": "",
                "Height": "",
                "LastNGames": "0",
                "LeagueID": "00",
                "Location": "",
                "Month": "0",
                "OpponentTeamID": "0",
                "Outcome": "",
                "PORound": "0",
                "PerMode": "PerGame",
                "Period": "0",
                "PlayerExperience": "",
                "PlayerPosition": "",
                "Season": "",
                "SeasonSegment": "",
                "SeasonType": "Regular Season",
                "ShotClockRange": "",
                "StarterBench": "",
                "TeamID": "0",
                "VsConference": "",
                "VsDivision": "",
                "Weight": ""
    }

    for season in season_list:
        payload["Season"] = season
        r = s.get(
                'https://stats.nba.com/stats/leaguedashplayerbiostats',
                params=payload,
                headers={
                        "Referer": "https://www.nba.com/",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                        },
                timeout=10
                )
        try:
            print(season, r)
            data = r.json()['resultSets'][0]
        except:
            print(season, r.reason, r)
        else:
            result = pd.DataFrame(data['rowSet'], columns = data['headers'])
            result = result.fillna(np.nan).replace('', np.nan)
            # convert draft year, draft round and draft number to a relative draft position in each year's draft
            result[['DRAFT_YEAR', 'DRAFT_ROUND', 'DRAFT_NUMBER']] = result[['DRAFT_YEAR', 'DRAFT_ROUND', 'DRAFT_NUMBER']].replace("Undrafted", np.nan).astype(float)
            result['DRAFT_POSITION'] = result.groupby(['DRAFT_YEAR']).DRAFT_NUMBER.transform(lambda x: (x - x.min()) / (x.max() - x.min()))
            # DRAFT_POSITION = 1 for undrafted players (last place in a year's draft)
            result['DRAFT_POSITION'] = result['DRAFT_POSITION'].fillna(1)
            # fix datatypes
            result.dropna(subset = ['PLAYER_ID', 'TEAM_ID'], inplace = True)
            result['PLAYER_ID'] = result.PLAYER_ID.astype(int).astype(str)
            result['TEAM_ID'] = result.TEAM_ID.astype(int).astype(str)
            try:
                result['PLAYER_WEIGHT'] = result.PLAYER_WEIGHT.astype(float)
            except ValueError as v:
                print("problem with PLAYER_WEIGHT:", v)
            else:
                result['SEASON'] = season
                output = pd.concat([output, result], axis = 0)
                time.sleep(time_sleep)
        
    s.close()
    return output
    
def retrieve_data(columns = None):    
    """retrieve latest player bio data to avoid multiple requests

    Returns:
        df: pandas dataframe of data
    """
    path = 'data/nba_playerbiostats.pkl'
    output = pd.read_pickle(f"https://github.com/WillKWL/nba_endpoint/blob/master/{path}?raw=true")
    print("Last committed: ", requests.get(f"https://api.github.com/repos/WillKWL/nba_endpoint/commits?path={path}").json()[0]['commit']['author']['date'])
    if columns is not None:
        output = output[columns]
    seasons = output.SEASON.unique()
    print(f"Data retrieved from {min(seasons)} to {max(seasons)}")
    return output

if __name__ == '__main__':
    
    choice = input("Retrieve latest data instead of sending requests? (y/n): ")
    if choice == 'y':
        data = retrieve_data()
        print(data.head())
    else:
        # grab latest data
        start_year = input('Start year? (YYYY: int)')
        end_year = input('End year? (YYYY: int)')
        if start_year == '':
            start_year = 1996
        if end_year == '':
            end_year = time.strftime("%Y")    
        output = request_data(int(start_year), int(end_year))
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        os.chdir('../data')
        output.to_pickle('nba_playerbiostats.pkl')
        print(f'{start_year} - {end_year} data saved to nba_playerbiostats.pkl')
