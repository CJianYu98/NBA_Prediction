import json
import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder

team_stats = {}

def get_nba_teams():
    print("Retrieving NBA teams...")
    nba_teams = pd.DataFrame(teams.get_teams())
    nba_team_abbr = nba_teams['abbreviation'].tolist()
    print("Succesfully retrieved NBA teams.")
    return nba_team_abbr

def populate_team_stats(nba_teams):
    print("Populating team stats...")
    for team in nba_teams:
        team_stats[team] = {
            "GAME_NO": 0,
            "AVG_PTS": 0,
            "AVG_AST": 0,
            "AVG_OREB": 0,
            "AVG_DREB": 0,
            "cPTS": 0,
            "cAST": 0,
            "cOREB": 0,
            "cDREB": 0,
            "cFGA": 0,
            "cTO": 0,
            "cFTA":0,
            "OFFRATE": 0,
            "DEFRATE": 0,
            "ELO": 1500
        }
    print("Successfully populated team stats.")
    return

def create_team_stats_json():
    print("Creating json file,,,")
    nba_teams = get_nba_teams()
    populate_team_stats(nba_teams)
    with open('data/team_stats.json', 'w') as json_file:
        json.dump(team_stats, json_file, indent=4)
    print("Successfully created json file.")
    return

def create_upcoming_games_csv():
    print("Creating csv file...")
    df = pd.DataFrame(columns=["HOME_TEAM", "AVG_PTS_x", "AVG_AST_x", "AVG_OREB_x", "AVG_DREB_x", "OFFRATE_x", "DEFRATE_x", "ELO_x", "AWAY_TEAM", "AVG_PTS_y", "AVG_AST_y", "AVG_OREB_y", "AVG_DREB_y", "OFFRATE_y", "DEFRATE_y", "ELO_y", "DIS_PTS", "DIS_AST", "DIS_OREB", "DIS_DREB", "DIS_OFFRATE", "DIS_DEFRATE", "DIS_ELO"])
    df.reset_index(drop=True,inplace=True)
    df.to_csv("data/upcoming_games.csv", index=False)
    print("Successfully created csv file.")
    return

def extract_nba_api():
    print("Extracting nba api data...")
    nba_teams = pd.DataFrame(teams.get_teams())
    team_ids = nba_teams['id'].unique()
    
    main_df = pd.DataFrame()
    for team_id in team_ids:
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
        games = gamefinder.get_data_frames()[0]
        games = games[(games['GAME_DATE'] >= '2020-12-22') & (games['WL'].isnull() == False)]
        main_df = main_df.append(games)
    
    main_df = main_df.sort_values('GAME_DATE',ascending=False)
    print("Successfully extracted nba api data.")
    return main_df

def clean_api_data(df):
    print("Cleaning nba api data...")
    df['length'] = df['MATCHUP'].str.len()
    df.sort_values('length', inplace=True)
    df.drop(columns=['length'], inplace=True)
    
    df_combined = df.merge(df, on='GAME_ID')
    df_combined = df_combined.drop(df_combined[df_combined['TEAM_ID_x'] == df_combined['TEAM_ID_y']].index)
    df_combined = df_combined.iloc[1:].iloc[::2]
    df_combined.reset_index(drop=True,inplace=True)
    df_combined.drop(columns=["SEASON_ID_x", "TEAM_ID_x", "SEASON_ID_y", "TEAM_ID_y", "MATCHUP_x", "MATCHUP_y"],inplace=True)
    df_combined = df_combined.replace(['W','L'], [int(1), int(0)]) # win = 1, lose = 0
    
    print("Successfully cleaned data.")
    return df_combined

def create_season_history_csv():
    print("Creating season history csv file...")
    df = extract_nba_api()
    df = clean_api_data(df)
    df['GAME_NO_x'] = 0
    df['GAME_NO_y'] = 0
    df['DIS_PTS'] = 0
    df['DIS_AST'] = 0
    df['DIS_OREB'] = 0
    df['DIS_DREB'] = 0
    df['DIS_OFFRATE'] = 0
    df['DIS_DEFRATE'] = 0
    df['DIS_ELO'] = 0
    
    df['GAME_DATE_x'] = pd.to_datetime(df['GAME_DATE_x']) # change GAME_DATE to datetime type
    df = df.sort_values(by = "GAME_DATE_x", ascending = True)
    
    with open("data/team_stats.json", 'r') as jsonFile:
        nba_teams = json.load(jsonFile)
    
    for i, row in df.iterrows():
    #         get the name of both teams
        team_1 = row['TEAM_ABBREVIATION_x']
        team_2 = row['TEAM_ABBREVIATION_y']

    #         add pre-game stats to row
        nba_teams[team_1]['GAME_NO'] += 1
        nba_teams[team_2]['GAME_NO'] += 1
        df.loc[i,'GAME_NO_x'] = nba_teams[team_1]['GAME_NO']
        df.loc[i,'GAME_NO_y'] = nba_teams[team_2]['GAME_NO']
        
        df.loc[i,'AVG_PTS_x'] = nba_teams[team_1]['AVG_PTS']
        df.loc[i,'AVG_PTS_y'] = nba_teams[team_2]['AVG_PTS']
        df.loc[i,'AVG_AST_x'] = nba_teams[team_1]['AVG_AST']
        df.loc[i,'AVG_AST_y'] = nba_teams[team_2]['AVG_AST']
        df.loc[i,'AVG_OREB_x'] = nba_teams[team_1]['AVG_OREB']
        df.loc[i,'AVG_OREB_y'] = nba_teams[team_2]['AVG_OREB']
        df.loc[i,'AVG_DREB_x'] = nba_teams[team_1]['AVG_DREB']
        df.loc[i,'AVG_DREB_y'] = nba_teams[team_2]['AVG_DREB']
        df.loc[i,'OFFRATE_x'] = nba_teams[team_1]['OFFRATE']
        df.loc[i,'OFFRATE_y'] = nba_teams[team_2]['OFFRATE']
        df.loc[i,'DEFRATE_x'] = nba_teams[team_1]['DEFRATE']
        df.loc[i,'DEFRATE_y'] = nba_teams[team_2]['DEFRATE']
        df.loc[i,'ELO_x'] = nba_teams[team_1]['ELO']
        df.loc[i,'ELO_y'] = nba_teams[team_2]['ELO']
        
        df.loc[i,'DIS_PTS'] = nba_teams[team_1]['AVG_PTS'] - nba_teams[team_2]['AVG_PTS']
        df.loc[i,'DIS_AST'] = nba_teams[team_1]['AVG_AST'] - nba_teams[team_2]['AVG_AST']
        df.loc[i,'DIS_OREB'] = nba_teams[team_1]['AVG_OREB'] - nba_teams[team_2]['AVG_OREB']
        df.loc[i,'DIS_DREB'] = nba_teams[team_1]['AVG_DREB'] - nba_teams[team_2]['AVG_DREB']
        df.loc[i,'DIS_OFFRATE'] = nba_teams[team_1]['OFFRATE'] - nba_teams[team_2]['OFFRATE']
        df.loc[i,'DIS_DEFRATE'] = nba_teams[team_1]['DEFRATE'] - nba_teams[team_2]['DEFRATE']    
        df.loc[i,'DIS_ELO'] = nba_teams[team_1]['ELO'] - nba_teams[team_2]['ELO']    

    #       update stats of both teams
        nba_teams[team_1]['cPTS'] += row['PTS_x']
        nba_teams[team_1]['cAST'] += row['AST_x']
        nba_teams[team_1]['cOREB'] += row['OREB_x']
        nba_teams[team_1]['cDREB'] += row['DREB_x']
        nba_teams[team_1]['cFGA'] += row['FGA_x']
        nba_teams[team_1]['cTO'] += row['TOV_x']
        nba_teams[team_1]['cFTA'] += row['FTA_x']
        
        nba_teams[team_1]['AVG_PTS'] = nba_teams[team_1]['cPTS'] /nba_teams[team_1]["GAME_NO"]
        nba_teams[team_1]['AVG_AST'] = nba_teams[team_1]['cAST']/nba_teams[team_1]["GAME_NO"]
        nba_teams[team_1]['AVG_OREB'] = nba_teams[team_1]['cOREB']/nba_teams[team_1]["GAME_NO"]
        nba_teams[team_1]['AVG_DREB'] = nba_teams[team_1]['cDREB']/nba_teams[team_1]["GAME_NO"]
        
        nba_teams[team_2]['cPTS'] += row['PTS_y']
        nba_teams[team_2]['cAST'] += row['AST_y']
        nba_teams[team_2]['cOREB'] += row['OREB_y']
        nba_teams[team_2]['cDREB'] += row['DREB_y']
        nba_teams[team_2]['cFGA'] += row['FGA_y']
        nba_teams[team_2]['cTO'] += row['TOV_y']
        nba_teams[team_2]['cFTA'] += row['FTA_y']
        
        nba_teams[team_2]['AVG_PTS'] = nba_teams[team_2]['cPTS'] /nba_teams[team_2]["GAME_NO"]
        nba_teams[team_2]['AVG_AST'] = nba_teams[team_2]['cAST']/nba_teams[team_2]["GAME_NO"]
        nba_teams[team_2]['AVG_OREB'] = nba_teams[team_2]['cOREB']/nba_teams[team_2]["GAME_NO"]
        nba_teams[team_2]['AVG_DREB'] = nba_teams[team_2]['cDREB']/nba_teams[team_2]["GAME_NO"]

    #       update OFF DEF ratings of both teams
        tot_pos_1 = nba_teams[team_1]['cFGA'] - nba_teams[team_1]['cOREB'] + nba_teams[team_1]['cTO'] +(0.4* nba_teams[team_1]['cFTA'])
        off_ratings_1 = nba_teams[team_1]['cPTS']/tot_pos_1
        nba_teams[team_1]['OFFRATE'] = off_ratings_1
        def_ratings_1 = nba_teams[team_2]['cPTS']/tot_pos_1
        nba_teams[team_1]['DEFRATE'] = def_ratings_1

        tot_pos_2 = nba_teams[team_2]['cFGA'] - nba_teams[team_2]['cOREB'] + nba_teams[team_2]['cTO'] +(0.4* nba_teams[team_2]['cFTA'])
        off_ratings_2 = nba_teams[team_2]['cPTS']/tot_pos_2
        nba_teams[team_2]['OFFRATE'] = off_ratings_2
        def_ratings_2 = nba_teams[team_1]['cPTS']/tot_pos_2
        nba_teams[team_2]['DEFRATE'] = def_ratings_2
                                 
    #       update ELO of both teams
        K_FACTOR = 20       # constant value for multiplier

        P_team = 1/(1 + 10 ** ((nba_teams[team_2]['ELO'] - nba_teams[team_1]['ELO'])/400))      # probability of team winning

        if row['WL_x'] == 1:
            elo_change = K_FACTOR * (1 - P_team)        # formula for change in elo if team 1 wins
        else:
            elo_change = K_FACTOR * (0 - P_team)        # formula for change in elo if team 1 loses

        nba_teams[team_1]['ELO'] += elo_change
        nba_teams[team_2]['ELO'] -= elo_change
        
    df.drop(df[(df['GAME_NO_x'] == 1) | (df['GAME_NO_y'] == 1 )].index, inplace=True) # omit first games of all teams
    
    with open("data/team_stats.json", 'w') as jsonFile:
        json.dump(nba_teams, jsonFile, indent=4)
    
    df.to_csv("data/season_history.csv", index=False)
    print("Successfully created season history csv file.")
    return


# ------------------------------------ DRIVERS ------------------------------------------------------------------------

# create_team_stats_json()
# create_upcoming_games_csv()
# create_season_history_csv()