import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import secrets
from utils import get_team_bar, get_all_player_bar, get_matchup_bar,fix_names, teams_dict, team_color, active_color, teams_dict, fix_long_names

####   CURRENT WEEK INPUTS   ####
tournament = "AT&T Byron Nelson"
current_week = 16                                                                                     # input current week variables
page_title = f"fx wk{current_week}"
matchup1 = ['AlphaWired','unit_circle']
matchup2 = ['Sneads Foot','Team Gamble']
matchup3 = ['txmoonshine','Philly919']
matchup4 = ['Putt Pirates','New Team 4']

#### ST, CSS, and PLOTLY CONFIGS
st.set_page_config(page_title=page_title, layout="centered", initial_sidebar_state="expanded")

with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

config = {'displayModeBar': False}

####  DG PROJECTIONS ####
dg_key = st.secrets.dg_key
path = f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}"

st.cache_data()
def get_projections():
    dg_proj = pd.read_csv(path)
    return dg_proj

dg_proj = get_projections()
dg_proj = dg_proj[['player_name','proj_points_total']]
dg_proj.columns = ['player','proj_pts']
dg_ = dg_proj.copy()
dg_proj.set_index(fix_names(dg_proj),inplace=True)  

####  FANTRAX TEAMS  ####
usecols=['Player','Status','Roster Status']
st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"week.csv",usecols=usecols)
    return teams

teams = get_fantrax()
teams.columns = ['player','team','active_reserve']
teams['team'] = teams.team.map(teams_dict)
teams.set_index('player',inplace=True)

####   MERGE TEAMS AND FANTRAX    ####
week = pd.merge(teams,dg_proj, left_index=True, right_index=True)

week[['player','team','active_reserve']] = week[
    ['player','team','active_reserve']
    ].astype('string')

week.sort_values('proj_pts',ascending=False,inplace=True)                                                   

####  LIST OF AVAILABLE PLAYERS  ####
available = pd.read_csv(r"available.csv",usecols=['Player']).Player.values
st.write("#")                                                                           # data loaded and ready


####  VERTICAL BAR - AVAILABLE PLAYERS  ####                                            # begin charts
dg_.set_index(fix_names(dg_),inplace=True)
dg_ = dg_[['proj_pts']]
available_bar_df = dg_[dg_.index.isin(available)].sort_values('proj_pts',ascending=True)[-5:]

available_bar = px.bar(
                available_bar_df,
                x=available_bar_df.proj_pts,
                title= "Top 5 Available",
                template='plotly_dark',
                color_continuous_scale=px.colors.sequential.Greys,
                color = 'proj_pts',
                text_auto='.1f',
                labels={'player':'','proj_pts':''},
                log_x=True,
                height=350
                )

available_bar.update_yaxes(tickfont=dict(color='#5A5856'))
available_bar.update_xaxes(showticklabels=False,showgrid=False, tickfont=dict(color='#5A5856'))
available_bar.update_layout(showlegend=False, coloraxis_showscale=False, title_x=.33, legend=dict(orientation='h',title='',y=1.3,x=.33))
available_bar.update_traces(width=.7)

# VERTICAL BAR - CURRENT ROSTERS                                                                            # begin make charts
top_6_active = pd.DataFrame()
for team in week.team.unique():
    temp = week[(week.team==team) & (week.active_reserve=='Active')][['team','player','proj_pts','active_reserve']]
    top_6_active = pd.concat([top_6_active,temp])

roster_projections_bar = px.bar(top_6_active.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
                    y='team',
                    x='proj_pts', 
                    color='team', 
                    template='plotly_dark',
                    text_auto='.3s',
                    labels = {'team': '', 'proj_pts':''},
                    color_discrete_map=team_color,
                    log_x=True,
                    height=350,
                    title='Projections'
                    ).update_layout(showlegend=False,title_x=.33,
                    ).update_xaxes(showticklabels=False
                    ).update_yaxes(tickfont=dict(color='#5A5856'),title_font_color='#5A5856',title_font_size=22)

# HORIZONTAL BAR - LINEUP COMPARISONS
top_6_proj = pd.DataFrame()
for team in week.team.unique():
    temp = week[week.team==team][['team','player','proj_pts','active_reserve']].sort_values(by='proj_pts',ascending=False)[:6]
    top_6_proj = pd.concat([top_6_proj,temp])

lineup_comparison_bar = px.bar(top_6_proj.sort_values(by = ['proj_pts','team'],ascending=False),
                               y = 'proj_pts',
                               color='team',
                                template='plotly_dark',
                                labels = {'index':" ",'player': '','proj_pts':''},
                                height=275,
                                color_discrete_map=team_color,
                                log_y=True,
                                ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
                                ).update_yaxes(showgrid=False,tickfont=dict(color='#5A5856')
                                ).update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))

# HORIZONTAL BAR = TOP 25 PLAYS
top25 = week.sort_values(by = 'proj_pts',ascending=False)[:25].reset_index(drop=True)
line = top25.proj_pts.mean()

top_25_bar = px.bar(top25,
                    y = 'proj_pts',
                    color = 'team',
                    color_discrete_map=team_color,
                    labels = {'index':"", 'proj_pts':'Projected Pts'},
                    text=week[:25].index,
                    template = 'plotly_dark',
                    height=275,
                    #   log_y=True,
                    hover_name='proj_pts'
                    ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
                    ).update_yaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856'
                    ).update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))


####  ROW 1 - TITLE AND ROSTERS  ####                                               # begin UI
col1,col2,col3 = st.columns(3)
with col1:
    st.markdown("#")
    st.markdown("")
    st.markdown("<center><h3>AT&T<br>Byron Nelson</h3></center>",unsafe_allow_html=True)
    st.markdown(f"<center>Week{current_week}</center>",unsafe_allow_html=True)
with col2:
    st.plotly_chart(roster_projections_bar,use_container_width=True,config = config)
with col3:
    st.plotly_chart(available_bar,use_container_width=True,config = config)
"---" 


#### ROW 2 - WIDE BAR CHARTS / TABS  ####  
st.markdown(f"<center>{len(week)} Rostered Players</center>",unsafe_allow_html=True) 

tab1, tab2, tab3 = st.tabs(['Top 25', 'Sit / Start', "Compare LU's"])
with tab1:
    st.plotly_chart(top_25_bar,use_container_width=True,config = config)
with tab2:
    st.plotly_chart(get_all_player_bar(week,'active_reserve',active_color),use_container_width=True,config = config)
with tab3:
    st.plotly_chart(lineup_comparison_bar,use_container_width=True,config = config)
"---" 


####  ROW 3 - ACTIVE RESERVE TABS  #### 
st.markdown(f"<center><h5>Active / Reserve Choices</center>",unsafe_allow_html=True) 
st.write("#")
team_tabs = st.tabs(list(teams_dict.keys()))
for tab, team_name in zip(team_tabs, teams_dict.values()):
        tab.plotly_chart(get_team_bar(week, team_name), use_container_width=True, config=config) 


#### ROW 3 - MATCHUP BAR CHARTS  ####
matchups_container = st.container(border=True)
with matchups_container:                                                                      
    st.markdown("<center><h5>Matchups</h4></center>",unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(get_matchup_bar(week,matchup1),use_container_width=True,config = config)
    with col2:
        st.plotly_chart(get_matchup_bar(week,matchup2),use_container_width=True,config = config)

    col1,col2 = st.columns(2)
    with col1:
        st.plotly_chart(get_matchup_bar(week,matchup3),use_container_width=True,config = config)
    with col2:
        st.plotly_chart(get_matchup_bar(week,matchup4),use_container_width=True,config = config)