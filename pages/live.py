import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt

from utils import get_rosters,get_matchups,highlight_rows,get_inside_cut,clean_leaderboard_column
from dict_utils import team_abbrev_dict,fix_names
from constants import LIVE_STATS,TOURNAMENT_NAME,WEEK_NUMBER

##### LIBRARY CONFIGs AND SECRETS KEYS #####

st.set_page_config(page_title="Live", layout="centered", initial_sidebar_state="expanded")              # streamlit
alt.themes.enable("dark")   

with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

config = {'displayModeBar': False}                                                                    # plotly

dg_key = st.secrets.dg_key               

## LIVE SCORING API ##
st.cache_data()
def get_live():
    live = round(pd.read_csv(LIVE_STATS),2)
    return live
live = get_live()
live = live.set_index(fix_names(live))


## CURRENT WEEK FANTASY ROSTERS & MATCHUPS ##
rosters = get_rosters()
matchups = get_matchups(WEEK_NUMBER-2)

fantrax = pd.merge(rosters,matchups,how='left',on='team')

inv_map = {v: k for k, v in team_abbrev_dict.items()}

fx = fantrax[['player_name','team','status','matchup']]
fx['team_short'] = fx['team'].map(inv_map)

teams = fx.loc[fx.status=='ACTIVE'].set_index('player_name')


## MERGE & PROCESS ##

# merge current fantasy teams and live scoring
live_merged = pd.merge(teams, live,how='left', left_index=True, right_index=True)[
    ['team','team_short','matchup', 'position','total','round', 'thru', 'sg_putt', 'sg_arg', 'sg_app', 'sg_ott','sg_t2g']] \
    .fillna(0).sort_values('total').convert_dtypes().reset_index()

live_merged['holes_remaining'] = (18 - (live_merged['thru']).fillna(0)).astype(int)
live_merged.loc[live_merged['position'].isin(['CUT', 'WD', 0]), 'holes_remaining'] = 0

live_merged = live_merged[live_merged['position'] !=0]




"#" # ensures refreshed page starts at top
# st.caption("updates when tournament starts")

st.markdown(f"<h3 style='text-align: center;'>{TOURNAMENT_NAME}</h3>", unsafe_allow_html=True)   
st.markdown(f"<center>Week {WEEK_NUMBER}</center>",unsafe_allow_html=True)
st.markdown("<center></center>",unsafe_allow_html=True)

# leaderboard and filter row
col1,blank,col2 = st.columns([3.6,.3,.9])
with col1:                                  # team leaderboard
    st.write("")
    placeholder = st.empty()

with col2:                                 # matchup filter
    matchup_num = st.multiselect(        
        label='Matchup',
        options=sorted(np.array(live_merged['matchup'].unique())),
        default=sorted(np.array(live_merged['matchup'].unique())),
    )
live_merged = live_merged[live_merged.matchup.isin(matchup_num)]


# 1 - team leaderboard
team_leaderboard = (
    live_merged[['team', 'team_short', 'total', 'holes_remaining', 'matchup']]
    .groupby(['team', 'team_short'])
    .agg({'total': 'sum', 'holes_remaining': 'sum'})
    .sort_values('total')
    .reset_index()
    )

team_leaderboard = (
    team_leaderboard
    .assign(inside_cut = team_leaderboard['team'].map(get_inside_cut(live_merged)).fillna(0).astype(int))
    .assign(total = team_leaderboard['total'].apply(lambda x: f"+{x}" if x > 0 else x)))
team_leaderboard['total'] = np.where(team_leaderboard['total'] == 0, "E", team_leaderboard['total']).astype(str)

team_leaderboard.drop(columns='team',inplace=True)
team_leaderboard.rename(columns={'team_short':'team'},inplace=True)
team_leaderboard.columns = ['Team','Total','PHR','Cut+']

team_leaderboard = team_leaderboard.T.style.apply(highlight_rows,axis=0)

# 2 - player leaderboard
player_leaderboard = live_merged[['player_name', 'total', 'position', 'round', 'thru','team','matchup']].fillna(0)

player_leaderboard[['total', 'round']] = player_leaderboard[['total', 'round']].apply(clean_leaderboard_column)
player_leaderboard['position'] = np.where(player_leaderboard['position'] == "WAITING", "-", player_leaderboard['position'])
player_leaderboard['thru'] = np.where(player_leaderboard['thru'] == 0, "-", player_leaderboard['thru']).astype(str)

player_leaderboard.columns = ['Player', 'Total', 'Pos', 'Rd', 'Thru', 'Team', 'Matchup']
player_leaderboard = player_leaderboard.style.set_properties(**{'font-weight': 'bold'}).apply(highlight_rows,axis=1)

# 3 - strokes gained table
strokes_gained_table = live_merged.groupby('team',as_index=False)[['sg_putt','sg_arg','sg_app','sg_t2g']].sum().reset_index(drop=True)
strokes_gained_table.columns = ['Team','SG Putt','SG Arg','SG App','SG T2G']
strokes_gained_table = strokes_gained_table.style.background_gradient(cmap='Greens').format(precision=2)


### UI ###
# header
st.markdown("<h5 style='text-align: center;;'>Live Leaderboard</h5>", unsafe_allow_html=True)

# team leaderboard
with placeholder:
    st.dataframe(team_leaderboard, 
                 hide_index=False,
                 height=180, 
                 use_container_width=True,
                 column_config={0:'',1:'1st',2:'2nd',3:'3rd',4:'4th',5:'5th',6:'6th',7:'7th',8:'8th'})

# strokes gained expander
with st.expander('click for Strokes Gained'):                                                                   
    st.dataframe(strokes_gained_table,
                 height=330,
                 hide_index=True,
                 use_container_width=True)
    
# player leaderboard
st.dataframe(player_leaderboard,                                                                                
             hide_index=True,
             height=1750,
             use_container_width=True,
             column_config={'Team':None,'Matchup':None})