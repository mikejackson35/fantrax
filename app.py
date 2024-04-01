import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import secrets
from utils import get_team_bar, get_all_player_bar, get_matchup_bar, fix_long_names, teams_dict, team_color, active_color, teams_dict

####   CURRENT WEEK INPUTS   ####
current_week = 13                                                                                      # input current week variables
page_title = f"Fantrax WK{current_week}"
tournament = "The Valero"
matchup1 = ['Sneads Foot','unit_circle']
matchup2 = ['Philly919','AlphaWired']
matchup3 = ['New Team 4','Team Gamble']
matchup4 = ['Putt Pirates','txmoonshine']

#### ST, CSS, and PLOTLY CONFIGS
st.set_page_config(page_title=page_title, layout="centered", initial_sidebar_state="expanded")

with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

config = {'displayModeBar': False}


####  LIVE SCORING API ####
# dg_key = st.secrets.dg_key
dg_key = "e297e933c3ad47d71ec1626c299e"

st.cache_data()
def get_projections():
    dg_proj = pd.read_csv(f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}")
    return dg_proj

dg_proj = get_projections()
dg_proj = dg_proj[['player_name','proj_points_total']]
dg_proj.columns = ['player','proj_pts']
dg_proj.set_index(fix_long_names(dg_proj).player,inplace=True)  

####  FANTRAX TEAMS  ####
usecols=['Player','Status','Roster Status']
st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"C:\Users\mikej\Desktop\fantrax\data\fantrax.csv",usecols=usecols)
    return teams

teams = get_fantrax()
teams.columns = ['player','team','active_reserve']
teams['team'] = teams.team.map(teams_dict)
teams.set_index('player',inplace=True)

####   MERGE DATA    ####
week = pd.merge(teams,dg_proj, left_index=True, right_index=True)

week[['player','team','active_reserve']] = week[
    ['player','team','active_reserve']
    ].astype('string')

week.sort_values('proj_pts',ascending=False,inplace=True)                                                   # data loaded and ready

# VERTICAL BAR - CURRENT ROSTERS                                                                            # begin make charts
top_6_active = pd.DataFrame()
for team in week.team.unique():
    temp = week[(week.team==team) & (week.active_reserve=='Active')][['team','player','proj_pts','active_reserve']]
    top_6_active = pd.concat([top_6_active,temp])
fig1 = px.bar(top_6_active.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
              y='team',
              x='proj_pts', 
              color='team', 
              template='plotly_dark',
              text_auto='.3s',
              labels = {'team': 'Current Rosters', 'proj_pts':''},
              color_discrete_map=team_color,
              log_x=True,
              height=325
              ).update_layout(showlegend=False
              ).update_xaxes(showticklabels=False
              ).update_yaxes(tickfont=dict(color='#5A5856'),title_font_color='#5A5856')

# VERTICAL BAR - OPTIMAL ROSTERS
top_6_proj = pd.DataFrame()
for team in week.team.unique():
    temp = week[week.team==team][['team','player','proj_pts','active_reserve']].sort_values(by='proj_pts',ascending=False)[:6]
    top_6_proj = pd.concat([top_6_proj,temp])
fig2 = px.bar(top_6_proj.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
              y = 'team',
              x = 'proj_pts',
              text_auto='.3s',
              color='team',
              template='plotly_dark',
              labels = {'team': 'Optimal Rosters', 'proj_pts':''},
              color_discrete_map=team_color,
              height=325,
              log_x=True
              ).update_layout(showlegend=False
              ).update_xaxes(showticklabels=False
              ).update_yaxes(tickfont=dict(color='#5A5856'),title_font_color='#5A5856')

# HORIZONTAL BAR - TOP 6 BY TEAM
fig3 = px.bar(top_6_proj.sort_values(by = ['proj_pts','team'],ascending=False),
              y = 'proj_pts',
              color='team',
            #   hover_name=top_6_proj.index,
              template='plotly_dark',
              labels = {'index':" ",'player': '','proj_pts':''},
              height=300,
              color_discrete_map=team_color,
              log_y=True,
              ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
              ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
              ).update_yaxes(showgrid=False,tickfont=dict(color='#5A5856')
              ).update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))

# HORIZONTAL BAR = TOP 25 PLAYS
top20 = week.sort_values(by = 'proj_pts',ascending=False)[:25].reset_index(drop=True)
line = top20.proj_pts.mean()
fig4 = px.bar(top20,
              y = 'proj_pts',
              color = 'team',
              color_discrete_map=team_color,
              labels = {'index':"", 'proj_pts':'Projected Pts'},
              text=week[:25].index,
              template = 'plotly_dark',
              height=300,
            #   log_y=True,
              hover_name='proj_pts'
              ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
              ).update_yaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856'
              ).update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))


####  ROW 1 - TITLE AND ROSTERS  ####                                                                              # ui row 1
col1,col2,col3 = st.columns(3)
with col1:
    st.markdown("###")
    st.markdown("###")
    st.caption(f"Fantrax Week {current_week}")
    st.markdown(f"<h4>{tournament}</h4>",unsafe_allow_html=True)
    st.markdown("###")
    st.markdown("###")
    st.markdown(f"{len(week)} Rostered Players",unsafe_allow_html=True)
with col2:
    st.plotly_chart(fig1,use_container_width=True,config = config)
with col3:
    st.plotly_chart(fig2, use_container_width=True,config = config)

#### ROW 2 - WIDE BAR CHARTS  ####  
st.markdown("<center><h3>OUTLOOK</h3></center>",unsafe_allow_html=True)                                                                                # ui row 2
tab_a, tab_b, tab_c = st.tabs(['Top 25 Plays', 'Sit / Start', 'Lineup Comparison'])
tab_a.plotly_chart(fig4,use_container_width=True,config = config)
tab_b.plotly_chart(get_all_player_bar(week,'active_reserve',active_color),use_container_width=True,config = config)
tab_c.plotly_chart(fig3,use_container_width=True,config = config)

#### ROW 3 - MATCHUP BAR CHARTS  ####                                                                               # ui row 3
st.markdown("<center><h3>MATCHUPS</h3></center>",unsafe_allow_html=True)
col1,col2 = st.columns(2)
with col1:
    col1.plotly_chart(get_matchup_bar(week,matchup1),use_container_width=True,config = config)
    col1.plotly_chart(get_matchup_bar(week,matchup2),use_container_width=True,config = config)
with col2:
    col2.plotly_chart(get_matchup_bar(week,matchup3),use_container_width=True,config = config)
    col2.plotly_chart(get_matchup_bar(week,matchup4),use_container_width=True,config = config)

####  ROW 4 - ACTIVE RESERVE TABS  ####                                                                             # ui row 4
st.markdown("<center><h3>ACTIVE/RESERVE CHOICES</h3></center>",unsafe_allow_html=True)
tab_objects = st.tabs(list(teams_dict.keys()))
for tab, team_name in zip(tab_objects, teams_dict.values()):
    tab.plotly_chart(get_team_bar(week, team_name), use_container_width=True, config=config) 