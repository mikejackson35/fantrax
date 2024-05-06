import os

import json
import requests

import pandas as pd
import numpy as np
import plotly.express as px

import streamlit as st
import secrets

from dict_utils import *

_dir_pkg_root = os.path.dirname(__file__)

dg_key = st.secrets.dg_key


def load_secrets():
    fn_secrets = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fantrax.secrets",
    )
    with open(fn_secrets, "r") as fsecrets:
        secrets = json.load(fsecrets)
    return secrets


def dump_to_json(fn_json, data):
    with open(fn_json, "w") as f_json:
        json.dump(data, f_json, indent=4)


def rest_request(url,body,note="",resp_format="json",):
    if resp_format == "json":
        headers = {"Content-Type": "application/json"}
    elif resp_format == "csv":
        headers = {"Content-Type": "application/csv"}

    response = requests.post(url,
                             data=json.dumps(body),
                             headers=headers,)
    print(f"{note}status code:", response.status_code)

    if resp_format == "json":
        return response.json()
    elif resp_format == "csv":
        return response.text
    else:
        return response

def fetch_leagueInfo(leagueId=None,secrets=load_secrets()):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_leagueInfo = (f"https://www.fantrax.com/fxea/general/getLeagueInfo?leagueId={leagueId}")
    body_leagueInfo = {}

    leagueInfo = rest_request(url_leagueInfo,
                              body_leagueInfo,
                              note="requesting league info. ")
    return leagueInfo

def fetch_teamRosters(
    leagueId=None,
    secrets=load_secrets(),
):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_teamRosters = (
        f"https://www.fantrax.com/fxea/general/getTeamRosters?leagueId={leagueId}"
    )
    body_teamRosters = {
        # "leagueId":secrets["league_id"],
    }
    teamRosters = rest_request(
        url_teamRosters,
        body_teamRosters,
        note="requesting team rosters. ",
    )
    return teamRosters

def fetch_leagueStandings(
    leagueId=None,
    secrets=load_secrets(),
):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_leagueStandings = (
        f"https://www.fantrax.com/fxea/general/getStandings?leagueId={leagueId}"
    )
    body_leagueStandings = {
        # "leagueId":secrets["league_id"],
    }
    leagueStandings = rest_request(
        url_leagueStandings,
        body_leagueStandings,
        note="requesting league standings. ",
    )
    return leagueStandings

def fetch_draftResults(
    leagueId=None,
    secrets=load_secrets(),
):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_draftResults = (
        f"https://www.fantrax.com/fxea/general/getDraftResults?leagueId={leagueId}"
    )
    body_draftResults = {
        # "leagueId":secrets["league_id"],
    }
    draftResults = rest_request(
        url_draftResults,
        body_draftResults,
        note="requesting draft results. ",
    )
    return draftResults



# get active/inactive rosters
def get_rosters():

    # get team names and team id's
    leagueInfo=fetch_leagueInfo()
    temp = leagueInfo['teamInfo'].values()
    team_ids = pd.DataFrame(temp).id.to_list()

    # get current active/inactive rosters
    teamRosters=fetch_teamRosters()

    # combine to create 'week' 
    rosters = []
    for id in team_ids:
        team_players = pd.DataFrame(teamRosters['rosters'][id]['rosterItems'])
        team_name = teamRosters['rosters'][id]['teamName']
        team_players['team'] = team_name
        rosters.append(team_players)

    rosters = pd.concat(rosters).set_index('id')

    # map in player names using their fantrax ids
    id_map = pd.read_csv(r"player_ids.csv",usecols=['player_name','player_id']).set_index('player_id')
    rosters = pd.merge(rosters, id_map, how='left', left_index=True, right_index=True).reset_index()[['player_name','team','status']]

    return rosters

# get weekly matchups
def get_matchups(week_num):
    leagueInfo=fetch_leagueInfo()

    matches = []
    for matchup in range(0,4):
        match = leagueInfo['matchups'][week_num]['matchupList'][matchup]
        matches.append([match['away']['name'], match['home']['name']])

    matchups = pd.DataFrame(matches, index=[1,2,3,4]).reset_index()
    matchups.columns = ['matchup','away','home']
    matchups['week'] = week_num

    matchups = matchups.melt(id_vars=['matchup','week'], value_name='team')[['team','matchup']]

    return matchups.convert_dtypes()

def fix_names(dg):
        names = dg['player_name'].str.split(expand=True)                  
        names[0] = names[0].str.rstrip(",")
        names[1] = names[1].str.rstrip(",")
        names['player_name'] = names[1] + " " + names[0]

        names['player_name'] = np.where(names['player_name']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Si Kim', 'Si Woo Kim', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Min Lee', 'Min Woo Lee', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Byeong An', 'Byeong Hun An', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Rooyen Van', 'Erik Van Rooyen', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Vince Whaley', 'Vincent Whaley', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='kevin Yu', 'Kevin Yu', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Kyounghoon Lee', 'Kyoung-Hoon Lee', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='Jr Hale', 'Blane Hale Jr', names['player_name'])
        names['player_name'] = np.where(names['player_name']=='de Dumont', 'Adrien Dumont de Chassart', names['player_name'])
        return names.player_name

def get_projections():
    path = f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}"
    projections = pd.read_csv(path, usecols=['player_name','proj_points_total'])
    projections['player_name'] = fix_names(projections)
    return projections

# # color dictionary
active_color={
    "ACTIVE":'rgb(146,146,143)',
    "RESERVE":'rgb(220,222,202)'
    }


def get_matchup_bar(rostered, week_num,matchup_num):

    all_matchups = get_matchups(week_num)
    one_matchup = all_matchups[all_matchups.matchup==matchup_num].team.to_list()

    matchup_bar = px.bar(rostered[(rostered.status=='ACTIVE') & (rostered.team.isin(one_matchup))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
                            y = 'proj_pts',
                            color = 'team',
                            color_discrete_map=team_color,
                            labels = {'_index':"", 'proj_pts':''},
                            text='player_name',
                            template = 'plotly_dark',
                            hover_name='proj_pts',
                            height=250,
                            log_y=True
                            ).update_xaxes(showticklabels=False,
                            ).update_yaxes(showticklabels=False,tickvals=[50,60,70,80,90,100], tickfont=dict(color='#5A5856')
                            ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856')
                            ).update_layout(legend=dict(orientation='h',title='',y=1.25,x=.1,font_color='#5A5856'))

    return matchup_bar

def get_team_bar(rostered, team):
    fig = px.bar(rostered[rostered.team == team].sort_values(by=['status','proj_pts'],ascending=[True,False]), 
                        x = 'player_name', 
                        y = 'proj_pts', 
                        height=250,
                        color='status', 
                        text_auto='.2s',
                        template = 'plotly_dark',
                        color_discrete_map=active_color,
                        log_y=True,
                        labels = {'proj_pts':'','player_name':""}
                        ).update_yaxes(showticklabels=False,showgrid=False, tickfont=dict(color='#5A5856')
                        ).update_xaxes(tickfont=dict(color='#5A5856')
                        ).update_layout(legend=dict(orientation='h',title='',y=1.3,x=.33)
                        ).update_traces(width=.7)
    return fig

def highlight_rows(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#e12729'
    elif value == 'Philly919':
        color = '#057dcd' # Aqua
    elif value == 'AlphaWired':
        color = '#ff595e' # Orange
    elif value == "Snead's Foot":
        color = '#82E0AA' # Green
    elif value == 'New Team 4':
        color = '#7f8c9b' # Red
    elif value == 'Team Gamble':
        color = '#2ECC71' # Navy
    elif value == 'txmoonshine':
        color = '#00bfff' # Yellow 
    elif value == 'u_c':
        color = '#e12729' # Purple
    elif value == '919':
        color = '#057dcd' # Aqua
    elif value == '[AW]':
        color = '#ff595e' # Orange
    elif value == 'NT 8':
        color = '#82E0AA' # Green
    elif value == 'NT 4':
        color = '#7f8c9b' # Red
    elif value == 'MG':
        color = '#2ECC71' # Navy
    elif value == 'txms':
        color = '#00bfff' # Yellow
    else:
        color = '#9ba6b1' # Grey
    return ['background-color: {}'.format(color) for r in row]


def plus_prefix(a):
    if a > 0:
        b = f"+{a}"
    else:
        b = a
    return b

def remove_T_from_positions(dataframe):
    """
    """
    dataframe['position'] = dataframe['position'].str.replace('T', '')
    return dataframe

def get_inside_cut(live_merged):
    """
    """
    live_merged = live_merged[live_merged['position'] != "WAITING"]
    live_merged = live_merged[live_merged['position'] != "CUT"]
    live_merged = remove_T_from_positions(live_merged)
    live_merged['position'] = live_merged['position'].dropna().astype('int')
    inside_cut_df = pd.DataFrame(live_merged[live_merged['position'] < 66].team.value_counts()).reset_index()
    inside_cut_df.columns = ['team','inside_cut']
    
    inside_cut_dict = dict(inside_cut_df.values)
    return inside_cut_dict

# Define a function to apply the transformations
def clean_leaderboard_column(x):
    x = x.apply(plus_prefix)
    x = np.where(x == 0, "  E", x)
    return x.astype(str)