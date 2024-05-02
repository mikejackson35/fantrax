import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import secrets


dg_key = st.secrets.dg_key    

def fix_names(live):
    """
    Takes in live datagolf scoring, cleans names, outputs list of active players this week
    """
    names = live['player'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player'] = names[1] + " " + names[0]

    names['player'] = np.where(names['player']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
    names['player'] = np.where(names['player']=='Si Kim', 'Si Woo Kim', names['player'])
    names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
    names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
    names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
    names['player'] = np.where(names['player']=='Vince Whaley', 'Vincent Whaley', names['player'])
    names['player'] = np.where(names['player']=='kevin Yu', 'Kevin Yu', names['player'])
    names['player'] = np.where(names['player']=='Kyounghoon Lee', 'Kyoung-Hoon Lee', names['player'])
    names['player'] = np.where(names['player']=='Jr Hale', 'Blane Hale Jr', names['player'])
    names['player'] = np.where(names['player']=='de Dumont', 'Adrien Dumont de Chassart', names['player'])
    return names.player


def highlight_rows(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#b22222' # Purple
    elif value == 'Philly919':
        color = '#1e90ff' # Aqua
    elif value == 'AlphaWired':
        color = '#ff0000' # Orange
    elif value == "Snead's Foot":
        color = '#82E0AA' # Green
    elif value == 'New Team 4':
        color = '#7f8c9b' # Red
    elif value == 'Team Gamble':
        color = '#2ECC71' # Navy
    elif value == 'txmoonshine':
        color = '#00bfff' # Yellow 
    else:
        color = '#9ba6b1' # Grey
    return ['background-color: {}'.format(color) for r in row]

def highlight_rows_team_short(row):
    value = row.loc['Team']
    if value == 'u_c':
        color = '#b22222' # Purple
    elif value == '919':
        color = '#1e90ff' # Aqua
    elif value == '[AW]':
        color = '#ff0000' # Orange
    elif value == 'NT 8':
        color = '#82E0AA' # Green
    elif value == 'NT 4':
        color = '#7f8c9b' # Red
    elif value == 'MG':
        color = '#2ECC71' # Navy
    elif value == 'txms':
        color = '#00bfff' # Yellow
    else:
        color = '#9ba6b1'  # Grey
    return ['background-color: {}'.format(color) for r in row]

teams_dict = {
        '919':'Philly919',
        'u_c':'unit_circle',
        'NT 4':'New Team 4',
        'NT 8':"Snead's Foot",
        'txms':'txmoonshine',
        'MG':'Team Gamble',
        'grrr':'Putt Pirates',
        '[AW]':'AlphaWired'
        }

matchups = {                                    # enter weekly matchups here
    'unit_circle':1,
    'Putt Pirates':2,
    'AlphaWired':1,
    'txmoonshine':3,
    'Sneads Foot':4,
    'New Team 4':2,
    'Team Gamble':4,
    'Philly919':3
}

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
    x = np.where(x == 0, "E", x)
    return x.astype(str)


#  IF WANT LIVE LEADERBOARD COLORS TO MATCH OTHER PAGES
# def highlight_rows(row):
#     value = row.loc['Team']
#     if value == 'unit_circle':
#         color = '#c28bdd' # Purple
#     elif value == 'Philly919':
#         color = '#0ec3d2' # Aqua
#     elif value == 'AlphaWired':
#         color = '#f7a05d' # Orange
#     elif value == 'Sneads Foot':
#         color = '#46d671' # Green
#     elif value == 'New Team 4':
#         color = '#f75e38' # Red
#     elif value == 'Team Gamble':
#         color = '#2693be' # Navy
#     elif value == 'txmoonshine':
#         color = '#dbc530' # Yellow
#     else:
#         color = '#73706a' # Grey
#     return ['background-color: {}'.format(color) for r in row]

# def highlight_rows_team_short(row):
#     value = row.loc['Team']
#     if value == 'u_c':
#         color = '#c28bdd' # Purple
#     elif value == '919':
#         color = '#0ec3d2' # Aqua
#     elif value == '[AW]':
#         color = '#f7a05d' # Orange
#     elif value == 'NT 8':
#         color = '#46d671' # Green
#     elif value == 'NT 4':
#         color = '#f75e38' # Red
#     elif value == 'MG':
#         color = '#2693be' # Navy
#     elif value == 'txms':
#         color = '#dbc530' # Yellow
#     else:
#         color = '#73706a' # Grey
#     return ['background-color: {}'.format(color) for r in row]