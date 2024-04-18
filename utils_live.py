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
    names['player'] = np.where(names['player']=='Kevin Yu', 'kevin Yu', names['player'])
    names['player'] = np.where(names['player']=='Kyounghoon Lee', 'Kyoung-Hoon Lee', names['player'])
    return names.player

def highlight_rows(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#2793bf' # Purple
    elif value == 'Philly919':
        color = '#26bf53' # Aqua
    elif value == 'AlphaWired':
        color = '#9ba6b1' # Orange
    elif value == 'Sneads Foot':
        color = '#2ad45c' # Green
    elif value == 'New Team 4':
        color = '#9ba6b1' # Red
    elif value == 'Team Gamble':
        color = '#26bf53' # Navy
    elif value == 'txmoonshine':
        color = '#26bf53' # Yellow 
    else:
        color = '#9ba6b1' # Grey
    return ['background-color: {}'.format(color) for r in row]

def highlight_rows_team_short(row):
    value = row.loc['Team']
    if value == 'u_c':
        color = '#2793bf' # Purple
    elif value == '919':
        color = '#26bf53' # Aqua
    elif value == '[AW]':
        color = '#9ba6b1' # Orange
    elif value == 'NT 8':
        color = '#2ad45c' # Green
    elif value == 'NT 4':
        color = '#9ba6b1' # Red
    elif value == 'MG':
        color = '#26bf53' # Navy
    elif value == 'txms':
        color = '#55b5dd' # Yellow
    else:
        color = '#9ba6b1'  # Grey
    return ['background-color: {}'.format(color) for r in row]

teams_dict = {
        '919':'Philly919',
        'u_c':'unit_circle',
        'NT 4':'New Team 4',
        'NT 8':'Sneads Foot',
        'txms':'txmoonshine',
        'MG':'Team Gamble',
        'grrr':'Putt Pirates',
        '[AW]':'AlphaWired'
        }

matchups = {                                    # enter weekly matchups here
    'unit_circle':1,
    'Putt Pirates':4,
    'AlphaWired':4,
    'txmoonshine':2,
    'Sneads Foot':2,
    'New Team 4':3,
    'Team Gamble':1,
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
    Remove 'T' from positions in a given column of a DataFrame.

    Parameters:
        dataframe (pandas.DataFrame): DataFrame containing the data.
        column_name (str): Name of the column containing positions.

    Returns:
        pandas.DataFrame: DataFrame with 'T' removed from positions in the specified column.
    """
    dataframe['position'] = dataframe['position'].str.replace('T', '')
    return dataframe

def get_inside_cut(live_merged):
    """
    Filter DataFrame based on position threshold and group by team.

    Parameters:
        dataframe (pandas.DataFrame): DataFrame containing the data.
        position_threshold (str): Threshold position for filtering.

    Returns:
        pandas.DataFrame: DataFrame with filtered data grouped by team.
    """
    live_merged = live_merged[live_merged['position'] != "WAITING"]
    live_merged = live_merged[live_merged['position'] != "CUT"]
    live_merged = remove_T_from_positions(live_merged)
    live_merged['position'] = live_merged['position'].dropna().astype('int')
    inside_cut_df = pd.DataFrame(live_merged[live_merged['position'] < 100].team.value_counts()).reset_index()
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