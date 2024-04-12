import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt
from utils_live import teams_dict, get_inside_cut, fix_names, highlight_rows_team_short,plus_prefix, matchups, highlight_rows, make_bold
import secrets

##### LIBRARY CONFIGs AND SECRETS KEYS #####

st.set_page_config(page_title="Live", layout="centered", initial_sidebar_state="expanded")              # streamlit
alt.themes.enable("dark")   

with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

config = {'displayModeBar': False}                                                                    # plotly

# dg_key = st.secrets.dg_key               
dg_key = 'e297e933c3ad47d71ec1626c299e'

## LIVE SCORING API ##
path = f"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key={dg_key}"

st.cache_data()
def get_live():
    live = round(pd.read_csv(path),2).rename(columns={'player_name':'player'})
    return live
live = get_live()
live = live.set_index(fix_names(live))


## CURRENT WEEK FANTASY ROSTERS & MATCHUPS ##
st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"week.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

teams.columns = ['player','team','active_reserve']
teams['team_short'] = teams['team']
teams['team'] = teams.team.map(teams_dict)
teams = teams.loc[teams.active_reserve=='Active'].set_index('player')


## MERGE & PROCESS ##

# merge current fantasy teams and live scoring
live_merged = pd.merge(teams, live, how='left', left_index=True, right_index=True)[['team','team_short','position','total','round','thru','sg_putt','sg_arg','sg_app','sg_ott','sg_t2g']].fillna(0).sort_values('total')
live_merged = live_merged.convert_dtypes().reset_index()
# add columns matchup_num & holes_remaining
live_merged['matchup_num'] = live_merged.team.map(matchups)
live_merged['holes_remaining'] = (72 - (live_merged['thru']).fillna(0)).astype(int)
live_merged.loc[live_merged['position'].isin(['CUT', 'WD']), 'holes_remaining'] = 0

"#" # ensures refreshed page starts at top
st.markdown("<h3 style='text-align: center;;'>The Masters</h3>", unsafe_allow_html=True)   
st.markdown("<center>Week 14</center>",unsafe_allow_html=True)
st.markdown("<center></center>",unsafe_allow_html=True)

# team leaderboard and matchup filter
col1,blank,col2 = st.columns([3.5,.5,.8])
with col1:
    st.write("")
    placeholder = st.empty()

with col2:
    matchup_num = st.multiselect(        
        label='Matchup',
        options=sorted(np.array(live_merged['matchup_num'].unique())),
        default=sorted(np.array(live_merged['matchup_num'].unique())),
    )

# data filtered by multiselect
live_merged = live_merged[live_merged.matchup_num.isin(matchup_num)]

# get team leaderboard
team_leaderboard = (live_merged[['team', 'team_short', 'total', 'holes_remaining', 'matchup_num']]
                    .groupby(['team', 'team_short'])
                    .agg({'total': 'sum', 'holes_remaining': 'sum'})
                    .sort_values('total')
                    .reset_index()
                   )

team_leaderboard['inside_cut'] = team_leaderboard['team'].map(get_inside_cut(live_merged)).fillna(0).astype(int)
# team_leaderboard['total'] = np.where(team_leaderboard['total'] == 0, "E", team_leaderboard['total'])#.astype(str)
team_leaderboard['total'] = team_leaderboard['total'].apply(plus_prefix)
team_leaderboard['total'] = np.where(team_leaderboard['total'] == 0, "E", team_leaderboard['total']).astype(str)
team_leaderboard_bar_df = team_leaderboard.copy()

team_leaderboard.drop(columns='team',inplace=True)
team_leaderboard.rename(columns={'team_short':'team'},inplace=True)
team_leaderboard.columns = ['Team','Total','PHR','Cut+']

team_leaderboard = team_leaderboard.T.style.apply(highlight_rows_team_short,axis=0)

# make player leaderboard
player_leaderboard = live_merged[['player', 'total', 'position', 'round', 'thru','team','matchup_num']].fillna(0)

# Define a function to apply the transformations
def transform_column(x):
    x = x.apply(plus_prefix)
    x[x == 0] = "E"
    return x.astype(str)

# Apply the transformations to 'total' and 'round' columns
player_leaderboard[['total', 'round']] = player_leaderboard[['total', 'round']].apply(transform_column)



# player_leaderboard['total'] = player_leaderboard['total'].apply(plus_prefix)
# player_leaderboard['total'] = np.where(player_leaderboard['total'] == 0, "E", player_leaderboard['total']).astype(str)

# player_leaderboard['round'] = player_leaderboard['round'].apply(plus_prefix)
# player_leaderboard['round'] = np.where(player_leaderboard['round'] == 0, "E", player_leaderboard['round']).astype(str)

player_leaderboard['position'] = np.where(player_leaderboard['position'] == "WAITING", "-", player_leaderboard['position'])
player_leaderboard['thru'] = np.where(player_leaderboard['thru'] == 0, "-", player_leaderboard['thru']).astype(str)

player_leaderboard.columns = ['Player','Total','Pos','Rd','Thru','Team','Matchup']
player_leaderboard = player_leaderboard.style.apply(highlight_rows,axis=1)

# strokes gained table
strokes_gained_table = live_merged.groupby('team',as_index=False)[['sg_putt','sg_arg','sg_app','sg_t2g']].sum().reset_index(drop=True)
strokes_gained_table.columns = ['Team','SG Putt','SG Arg','SG App','SG T2G']
strokes_gained_table = strokes_gained_table.style.background_gradient(cmap='Greens').format(precision=2)

### UI ###
# header
st.markdown("<h5 style='text-align: center;;'></h5>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;;'></h5>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;;'></h5>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;;'></h5>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;;'>Live Leaderboard</h5>", unsafe_allow_html=True)

# team leaderboard
with placeholder:
    st.dataframe(team_leaderboard,                                                                   
                                hide_index=False,height=180, use_container_width=True,
                                column_config={0:'',1:'1st',2:'2nd',3:'3rd',4:'4th',5:'5th',6:'6th',7:'7th',8:'8th'})

# strokes gained expander
with st.expander('EXPAND for Strokes Gained by Team'):                                                                   
    st.dataframe(strokes_gained_table,
                 height=330,hide_index=True,use_container_width=True)
    
# player leaderboard
st.dataframe(player_leaderboard,                                                                                
             hide_index=True,height=1750,use_container_width=True,
             column_config={'Team':None,'Matchup':None})