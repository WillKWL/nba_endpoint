import requests
from itertools import combinations
from tqdm import tqdm
import pandas as pd
import time
import os

home_road_list = ["Home", "Road"]


def get_data(start_year, end_year, team_list = None):
    s = requests.Session()
    output = None
    fail_list = []
    season_list = [str(i) + '-' + str(i+1)[2:] for i in range(start_year, end_year)]
    if team_list is None:
        team_list = ['1610612742', '1610612765', '1610612763', '1610612749', '1610612762', '1610612755', '1610612737', '1610612757', '1610612752', '1610612748', '1610612738', '1610612753', '1610612744', '1610612743', '1610612766', '1610612754', '1610612760', '1610612739', '1610612764', '1610612759', '1610612756', '1610612761', '1610612741', '1610612758', '1610612746', '1610612745', '1610612747', '1610612750', '1610612751', '1610612740']
    
    with tqdm(total=len(list(combinations(team_list, 2))) * len(season_list) * 2) as progress_bar:
        for season in season_list:
            for team, opponent in combinations(team_list, 2):
                for home_road in home_road_list:
                    payload = {
                        ## basic settings
                        "MeasureType": "Base", # for target variable, just the BASE statistics are enough
                        "PerMode": "PerGame", # keep it as per game but turn pace adjust to Y for stats per 100 possession, cannot use Per100Posessions here as it will mess up the minutes played per lineup
                        "PaceAdjust": "Y",
                        "Season": season, # iterate over all seasons
                        "SeasonType": "Regular Season",
                        "SeasonSegment": "Post All-Star",

                        ## interesting to look at 
                        'DateFrom': '',
                        'DateTo': '',
                        "GroupQuantity": "5", # 5/4/3/2-player lineup
                        "Location": home_road, # "", "Home", "Road", iterate over "Home" and "Road"
                        "OpponentTeamID": opponent, # iterate over all opponents
                        "TeamID": team, # iterative over all teams

                        ## ignore for now
                        'Conference': '',
                        "Division": "",
                        "GameSegment": "", # 1st half, 2nd half
                        "LastNGames": "0",
                        "LeagueID": "00",
                        "Month": "0",
                        "Outcome": "", # won't be able to know in advance
                        "Period": "0", # 1Q, 2Q, 3Q, 4Q
                        "PlusMinus": "N",
                        "PORound": "0",
                        "Rank": "N",
                        "ShotClockRange": "",
                        "VsConference": "",
                        "VsDivision": ""
                    }

                    try:
                        r = s.get('https://stats.nba.com/stats/leaguedashlineups',
                                        params=payload,
                                        headers={
                                            "Referer": "https://www.nba.com/",
                                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                                            },
                                        timeout=10)
                    
                    
                        # print('\n', season, home_road, team, opponent, r)
                        data = r.json()['resultSets'][0]
                    except TimeoutError as t:
                        print(season, home_road, team, opponent, t)
                        fail_list.append([season, home_road, team, opponent])
                        result = pd.DataFrame()
                    else:
                        try:
                            result = pd.DataFrame(data['rowSet'], columns = data['headers'])
                            result[['SEASON']] = season
                            result[['LOCATION']] = home_road
                            result[['OPPONENT_TEAM_ID']] = opponent
                            result['TEAM_ID'] = result['TEAM_ID'].astype(str)
                            result = pd.concat([
                                result.GROUP_ID.str.strip('-').str.split('-', expand=True).rename(columns = lambda x: 'PlayerID_' + str(x)), 
                                result.GROUP_NAME.str.strip('-').str.split(' - ', expand=True).rename(columns = lambda x: 'PlayerName_' + str(x)), 
                                result.drop(columns = ['GROUP_ID', 'GROUP_NAME'])
                                ], axis = 1)
                        except:
                            fail_list.append([season, home_road, team, opponent])
                            result = pd.DataFrame()
                    
                    output = pd.concat([output, result], axis = 0)
                    time.sleep(1)
                    progress_bar.update(1)
    
    s.close()
    return output, fail_list
    
if __name__ == '__main__':
    # grab latest data
    start_year = 2007
    end_year = input('2007 until which year? (YYYY: int)')
    if end_year == '':
        end_year = time.strftime("%Y")
    
    data, fail_list = get_data(int(start_year), int(end_year), 
                            #    team_list = ['1610612737', '1610612738']
                               )
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)
    os.chdir('../data')
    data.to_pickle('nba_lineupstats.pkl')
    print(f'{start_year} - {end_year} data saved to nba_lineupstats.pkl')
    print(f'failed to get: {fail_list}')