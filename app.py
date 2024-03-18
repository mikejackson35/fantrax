import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import secrets
from utils import get_team_bar, get_all_player_bar, get_matchup_bar, fix_long_names, teams_dict, team_color, active_color

st.set_page_config(
    page_title="Fantrax Wk11",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
config = {'displayModeBar': False}


####  LIVE SCORING DATA FROM DATAGOLF API AND PREP FOR MERGE  ####
dg_key = st.secrets.dg_key
st.cache_data()
def get_projections():

    dg_proj = pd.read_csv(f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}")
    return dg_proj
dg_proj = get_projections()
dg_proj = dg_proj[['player_name','proj_points_total']]
dg_proj.columns = ['player','proj_pts']
dg_proj.set_index(fix_long_names(dg_proj).player,inplace=True)  


####  FANTRAX TEAMS CSV DOWNLOAD AND PREP FOR MERGE  ####
usecols=['Player','Status','Roster Status']
st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fantrax.csv",
                        usecols=usecols)
    return teams
teams = get_fantrax()
teams.columns = ['player','team','active_reserve']
teams['team'] = teams.team.map(teams_dict)
teams.set_index('player',inplace=True)

####   MERGE DATA    ####
week = pd.merge(teams,dg_proj, left_index=True, right_index=True)
week[['player','team','active_reserve']] = week[['player','team','active_reserve']].astype('string')
week.sort_values('proj_pts',ascending=False,inplace=True)

####   CURRENT WEEK INPUTS   ####
current_week = 11
tournament = "Valspar<br>Championship"
matchup1 = ['Putt Pirates','unit_circle']
matchup2 = ['txmoonshine','AlphaWired']
matchup3 = ['Team Gamble','Philly919']
matchup4 = ['New Team 4','Sneads Foot']   
num_players = len(week)

#### MAKE CHARTS ####

# VERTICAL BAR - CURRENT ROSTERS
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
              ).update_yaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856'#,tickvals=[60,70,80,90]
              ).update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))



####  ROW 1 - TITLE AND ROSTERS  ####
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
tab1, tab2, tab3 = st.tabs(['Top 25 Plays', 'Sit / Start', 'Optimals'])
# tab1.plotly_chart(get_all_player_bar(week,'team',team_color),use_container_width=True,config = config)
tab1.plotly_chart(fig4,use_container_width=True,config = config)
tab2.plotly_chart(get_all_player_bar(week,'active_reserve',active_color),use_container_width=True,config = config)
tab3.plotly_chart(fig3,use_container_width=True,config = config)

#### ROW 3 - MATCHUP BAR CHARTS  ####
st.markdown("<center><h3>MATCHUPS</h3></center>",unsafe_allow_html=True)
col1,col2 = st.columns(2)
with col1:
    col1.plotly_chart(get_matchup_bar(week,matchup1),use_container_width=True,config = config)
    col1.plotly_chart(get_matchup_bar(week,matchup2),use_container_width=True,config = config)
with col2:
    col2.plotly_chart(get_matchup_bar(week,matchup3),use_container_width=True,config = config)
    col2.plotly_chart(get_matchup_bar(week,matchup4),use_container_width=True,config = config)

####  ROW 4 - ACTIVE RESERVE TABS  ####
st.markdown("<center><h3>ACTIVE/RESERVE CHOICES</h3></center>",unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['919', 'u_c', 'txms','[AW]','NT4','MG','foot','grrr'])
tab1.plotly_chart(get_team_bar(week,'Philly919'),use_container_width=True,config = config)
tab2.plotly_chart(get_team_bar(week,'unit_circle'),use_container_width=True,config = config)
tab3.plotly_chart(get_team_bar(week,'txmoonshine'),use_container_width=True,config = config)
tab4.plotly_chart(get_team_bar(week,'AlphaWired'),use_container_width=True,config = config)
tab5.plotly_chart(get_team_bar(week,'New Team 4'),use_container_width=True,config = config)
tab6.plotly_chart(get_team_bar(week,'Team Gamble'),use_container_width=True,config = config)
tab7.plotly_chart(get_team_bar(week,'Sneads Foot'),use_container_width=True,config = config)
tab8.plotly_chart(get_team_bar(week,'Putt Pirates'),use_container_width=True,config = config)    