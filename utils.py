import pandas as pd
import numpy as np

import plotly.express as px
import streamlit as st

from dict_utils import team_color,active_color,fix_names
from constants import FANTASY_PROJECTIONS
from utils_api import fetch_leagueInfo,fetch_teamRosters

def get_rosters():

    """
    Input: None

    Output: dataframe of current week rosters
    """

    leagueInfo=fetch_leagueInfo()                               # get team names and team id's
    temp = leagueInfo['teamInfo'].values()
    team_ids = pd.DataFrame(temp).id.to_list()                  # get current active/inactive rosters
    teamRosters=fetch_teamRosters()

    rosters = []                                                # combine to create 'rosters' 
    for id in team_ids:
        team_players = pd.DataFrame(
            teamRosters['rosters'][id]['rosterItems'])
        team_name = teamRosters['rosters'][id]['teamName']
        team_players['team'] = team_name
        rosters.append(team_players)
    rosters = pd.concat(rosters).set_index('id')

    id_map = pd.read_csv(r"player_ids.csv",                     # map in fantrax player names
                         usecols=['player_name','player_id']
                         ).set_index('player_id')
    rosters = pd.merge(rosters, id_map,
                       how='left',
                       left_index=True, right_index=True
                       ).reset_index()[
                           ['player_name','team','status']]

    return rosters

def get_matchups(WEEK_NUMBER):

    """
    Input:  WEEK_NUMBER (from contstants.py)

    Output: long format (melted) dataframe 
            showing week number, team name, and matchup number
    """

    leagueInfo=fetch_leagueInfo()

    matches = []
    for matchup in range(0,4):
        match = leagueInfo['matchups'][WEEK_NUMBER]['matchupList'][matchup]
        matches.append([match['away']['name'], match['home']['name']])

    matchups = pd.DataFrame(matches, index=[1,2,3,4]).reset_index()
    matchups.columns = ['matchup','away','home']
    matchups['week'] = WEEK_NUMBER

    matchups = matchups.melt(id_vars=['matchup','week'],
                             value_name='team')[
                                 ['team','matchup']]

    return matchups.convert_dtypes()


def get_projections():

    """
    Input:  None

    Output: dataframe of current week datagolf projections. DG player 
        names converted to fantrax first-last format
    """

    projections = pd.read_csv(FANTASY_PROJECTIONS,
                              usecols=['player_name','proj_points_total'])
    projections['player_name'] = fix_names(projections)
    return projections


def get_matchup_bar(rostered, week_num, matchup_num):

    """
    Input: dataframe of current week rosters, week number (int),
            and matchup number (int)

    Output: plolty express bar chart showing the two teams in user 
            specified matchup number
    """

    all_matchups = get_matchups(week_num)
    one_matchup = all_matchups[all_matchups.matchup==matchup_num].team.to_list()

    matchup_bar = px.bar(rostered
                        [(rostered.status=='ACTIVE') & 
                         (rostered.team.isin(one_matchup))]
                        .sort_values(by = 'proj_pts',ascending=False)
                        .reset_index(),
                        y = 'proj_pts',
                        color = 'team',
                        color_discrete_map=team_color,
                        labels = {'_index':"", 'proj_pts':''},
                        text='player_name',
                        template = 'presentation',
                        hover_name='proj_pts',
                        height=250,
                        log_y=True
                        ).update_xaxes(showticklabels=False,
                        ).update_yaxes(showticklabels=False,
                                       tickvals=[50,60,70,80,90,100],
                                       tickfont=dict(color='#5A5856')
                        ).update_yaxes(gridcolor="#B1A999", 
                                       tickfont=dict(color='#5A5856')
                        ).update_layout(legend=dict(
                                        orientation='h',title='',
                                        y=1.25,x=.1,
                                        font_color='#5A5856'))

    return matchup_bar

def get_team_bar(rostered, team):

    """
    Input:  dataframe of current week rosters and team name (str)

    Output: plotly bar chart showing all available players this
            week for a single team
    """

    fig = px.bar(rostered[rostered.team == team]
                 .sort_values(by=['status','proj_pts'],ascending=[True,False]), 
                        x = 'player_name', 
                        y = 'proj_pts', 
                        height=250,
                        color='status', 
                        text_auto='.2s',
                        template = 'presentation',
                        color_discrete_map=active_color,
                        log_y=True,
                        labels = {'proj_pts':'','player_name':""},
                        hover_name='player_name'
                        ).update_yaxes(showticklabels=False,showgrid=False,
                                       tickfont=dict(color='#5A5856')
                        ).update_xaxes(tickfont=dict(color='#5A5856')
                        ).update_layout(legend=dict(orientation='h',
                                                    title='',y=1.3,x=.33)
                        ).update_traces(width=.7, textfont_size=12, textfont_family='Arial Black')
    return fig


def highlight_rows(row):

    """
    Input: 'Team' column of live leaderboard dataframe

    Output: css background color for specified 'Team'
    """

    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#32cd32'
    elif value == 'Philly919':
        color = '#00bfff' # Aqua
    elif value == 'AlphaWired':
        color = '#7f8c9b' # Orange
    elif value == "Snead's Foot":
        color = '#1e90ff' # Green
    elif value == 'New Team 4':
        color = '#a9a9a9' # Red
    elif value == 'Team Gamble':
        color = '#dc143c' # Navy
    elif value == 'txmoonshine':
        color = '#228b22' # Yellow 
    elif value == 'u_c':
        color = '#32cd32' # Purple
    elif value == '919':
        color = '#00bfff' # Aqua
    elif value == '[AW]':
        color = '#7f8c9b' # Orange
    elif value == 'NT 8':
        color = '#1e90ff' # Green
    elif value == 'NT 4':
        color = '#a9a9a9' # Red
    elif value == 'MG':
        color = '#dc143c' # Navy
    elif value == 'txms':
        color = '#228b22' # Yellow
    else:
        color = '#b22222' # Grey
    return ['background-color: {}'.format(color) for r in row]

    # if value == 'unit_circle':
    #     color = '#a9a9a9'
    # elif value == 'Philly919':
    #     color = '#00bfff' # Aqua
    # elif value == 'AlphaWired':
    #     color = '#1e90ff' # Orange
    # elif value == "Snead's Foot":
    #     color = '#7f8c9b' # Green
    # elif value == 'New Team 4':
    #     color = '#228b22' # Red
    # elif value == 'Team Gamble':
    #     color = '#32cd32' # Navy
    # elif value == 'txmoonshine':
    #     color = '#dc143c' # Yellow 
    # elif value == 'u_c':
    #     color = '#a9a9a9' # Purple
    # elif value == '919':
    #     color = '#00bfff' # Aqua
    # elif value == '[AW]':
    #     color = '#1e90ff' # Orange
    # elif value == 'NT 8':
    #     color = '#7f8c9b' # Green
    # elif value == 'NT 4':
    #     color = '#228b22' # Red
    # elif value == 'MG':
    #     color = '#32cd32' # Navy
    # elif value == 'txms':
    #     color = '#dc143c' # Yellow
    # else:
    #     color = '#b22222' # Grey



def get_inside_cut(live_merged):

    """
    Input:  dataframe live_merged

    Output: dictionary {team: count of players inside the cutline}
    """

    # Filter out rows where 'position' is "CUT", "WAITING", or "WD"
    live_merged = live_merged[(live_merged['position'] != "CUT") & 
                              (live_merged['position'] != "WAITING") & 
                              (live_merged['position'] != "WD")]

    # Apply lambda function to remove 'T', drop NaN values, and convert to integer
    live_merged.loc[:, 'position'] = live_merged['position'].apply(lambda x: x.replace('T', '')).dropna().astype('int')

    # Create a dataframe with counts of players inside the cutline per team
    inside_cut_df = pd.DataFrame(live_merged[live_merged['position'] < 51].team.value_counts()).reset_index()
    inside_cut_df.columns = ['team', 'inside_cut']

    # Convert the dataframe to a dictionary
    inside_cut_dict = dict(inside_cut_df.values)
    return inside_cut_dict

def clean_leaderboard_column(column):

    """
    Input:  any numberic column of live leaderboard

    Output: clean column as strings with "+", "E", etc formatting
    """

    column = column.apply(lambda x: f"+{x}" if x > 0 else x)
    column = np.where(column == 0, "  E", column)
    return column.astype(str)

# Define the bold_font function
def bold_font(val):
    return 'font-weight: bold; font-family: Arial; color: white;'