import numpy as np
import pandas as pd
import plotly.express as px

import streamlit as st

from utils import get_rosters,get_matchups,get_projections,get_matchup_bar,get_team_bar
from dict_utils import team_color,active_color,team_abbrev_dict
from constants import TOURNAMENT_NAME,WEEK_NUMBER

page_title = f"fx wk {WEEK_NUMBER}"

#### CONFIGS - streamlit, css, plotly  ####
st.set_page_config(page_title=page_title, layout="wide", initial_sidebar_state="expanded")

with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

config = {'displayModeBar': False}
template = 'presentation'


#### READ IN DATA, MERGE, AND CLEAN  ####
rosters = get_rosters()
matchups = get_matchups(WEEK_NUMBER)
projections = get_projections()

fantrax = pd.merge(rosters,matchups,how='left',on='team')
rostered = pd.merge(fantrax,projections,how='left',on='player_name').dropna().sort_values('proj_points_total',ascending=False).reset_index(drop=True)
rostered.columns = ['player_name','team','status','matchup','proj_pts']

st.write("#")   # ensures page re-loads at top

####  VERTICAL BAR - AVAILABLE PLAYERS  ####
rostered_filter = rostered.player_name.to_list()
available = projections[~projections.player_name.isin(rostered_filter)].sort_values('proj_points_total',ascending=True)[-8:]
available.columns = ['player_name','proj_pts']

available_bar = px.bar(
                available.set_index('player_name'),
                x='proj_pts',
                title= "Best Available",
                template=template,
                color_continuous_scale=px.colors.sequential.Greys,
                color = 'proj_pts',
                text_auto='.0f',
                labels={'player_name':'','proj_pts':''},
                log_x=True,
                height=600,
                )

available_bar.update_yaxes(tickfont=dict(color='#5A5856'))
available_bar.update_xaxes(showticklabels=False,showgrid=False, tickfont=dict(color='#5A5856'))
available_bar.update_layout(showlegend=False, coloraxis_showscale=False, title_x=.33, legend=dict(orientation='h',title='',y=1.3,x=.33))
available_bar.update_traces(width=.7)


# VERTICAL BAR - CURRENT ROSTERS                                                              
top_6_active = pd.DataFrame()
for team in rostered.team.unique():
    temp = rostered[(rostered.team==team) & (rostered.status=='ACTIVE')][['team','player_name','proj_pts','status']]
    top_6_active = pd.concat([top_6_active,temp])

roster_projections_bar = px.bar(top_6_active.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
                    y='team',
                    x='proj_pts', 
                    color='team', 
                    template=template,
                    text_auto='.3s',
                    labels = {'team': '', 'proj_pts':''},
                    color_discrete_map=team_color,
                    log_x=True,
                    height=600,
                    title='Projections',
                    # width=500
                    )
roster_projections_bar.update_layout(showlegend=False,title_x=.33 )
roster_projections_bar.update_xaxes(showticklabels=False)
roster_projections_bar.update_yaxes(tickfont=dict(color='#5A5856'),title_font_color='#5A5856',title_font_size=22)


# HORIZONTAL BAR - LINEUP COMPARISONS (optimals)
top_6_proj = pd.DataFrame()
for team in rostered.team.unique():
    temp = rostered[rostered.team==team][['team','player_name','proj_pts','status']].sort_values(by='proj_pts',ascending=False)[:6]
    top_6_proj = pd.concat([top_6_proj,temp])

best_projected_lineup_bar = px.bar(top_6_proj,
                                    x='player_name',
                                    y='proj_pts',
                                    color='team',
                                    template=template,
                                    labels = {'index':" ",'player_name': '','proj_pts':''},
                                    height=350,
                                    color_discrete_map=team_color,
                                    hover_name='player_name',
                                    text_auto='.2s'
                                    )

best_projected_lineup_bar.add_hline(y=np.median(top_6_proj.proj_pts),line_color='white', line_dash="dot",annotation_text='Median Optimal Lineups')
best_projected_lineup_bar.update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856'))
best_projected_lineup_bar.update_yaxes(showgrid=False,tickfont=dict(color='#5A5856'))
best_projected_lineup_bar.update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))



# HORIZONTAL BAR - TOP 25 PLAYS
top25 = rostered.reset_index(drop=True)

top_25_bar = px.bar(top25,
                    y = 'proj_pts',
                    color = 'team',
                    color_discrete_map=team_color,
                    labels = {'index':"", 'proj_pts':'Projected Pts'},
                    text='player_name',
                    template = template,
                    height=350,
                    hover_name='proj_pts'
                    )

top_25_bar.add_hline(y=np.median(rostered.proj_pts),line_color='white', line_dash="dot",annotation_text="Median All Rostered Players")
top_25_bar.update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856'))
top_25_bar.update_yaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856')
top_25_bar.update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))



# HORIZONTAL BAR - ACTIVE/INACTIVE PLAYERS
playing_this_week = projections[projections.player_name.isin(rostered_filter)].sort_values('proj_points_total',ascending=False).reset_index(drop=True)
playing_this_week.columns = ['player_name','proj_pts']

temp = rostered[['player_name','status']]
playing_this_week = pd.merge(playing_this_week,temp,how='left',on='player_name').convert_dtypes()

all_player_bar = px.bar(playing_this_week,
                        # x = rostered.index,
                        y = 'proj_pts',
                        template=template,
                        color = 'status',
                        color_discrete_map=active_color,
                        labels = {'index':"", 'proj_pts':''},
                        height=350,
                        # log_y=True,
                        hover_name=playing_this_week.player_name)

all_player_bar.add_hline(y=np.median(rostered.proj_pts),line_color='white', line_dash="dot",annotation_text="Median All Rostered Players")
all_player_bar.update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856'))
all_player_bar.update_yaxes(showgrid=False,tickfont=dict(color='#5A5856'))
all_player_bar.update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))


# begin UI

####  HEADER  ####
st.markdown(f"<center>Week {WEEK_NUMBER-1}</center>",unsafe_allow_html=True)
st.markdown(f"<center><h1>{TOURNAMENT_NAME}</h1></center>",unsafe_allow_html=True)
st.markdown(f"<center>{len(rostered)} Rostered Players</center>",unsafe_allow_html=True)

#### ROW 1 - WIDE BAR CHARTS / TABS  ####  
st.markdown("#")
st.markdown("") 

col1,col2,blank,col3 = st.columns([1.25,1.25,.5,3.5])
with col1:
    st.plotly_chart(roster_projections_bar,use_container_width=True,config = config)
with col2:
    st.plotly_chart(available_bar,use_container_width=True,config = config)
with blank:
    st.write(" ")
with col3:
    matchups_container = st.container(border=True)
    with matchups_container:                                                                      
        st.markdown("<center><h5>Matchups</h4></center>",unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            st.plotly_chart(get_matchup_bar(rostered,WEEK_NUMBER-1,1),use_container_width=True,config = config)
        with col2:
            st.plotly_chart(get_matchup_bar(rostered,WEEK_NUMBER-1,2),use_container_width=True,config = config)

        col1,col2 = st.columns(2)
        with col1:
            st.plotly_chart(get_matchup_bar(rostered,WEEK_NUMBER-1,3),use_container_width=True,config = config)
        with col2:
            st.plotly_chart(get_matchup_bar(rostered,WEEK_NUMBER-1,4),use_container_width=True,config = config)

st.write("##")
st.write("##")
st.write("##")

####  ROW 2 - WIDE BAR CHARTS / TABS  #### 
st.markdown(f"<center><h5>Overview</center>",unsafe_allow_html=True) 
st.write("#")

tab1, tab2, tab3 = st.tabs(['Rostered Players', 'Sit / Start', "Optimal LU's"])
with tab1:
    st.plotly_chart(top_25_bar,use_container_width=True,config = config)
with tab2:
    st.plotly_chart(all_player_bar,use_container_width=True,config = config)
with tab3:
    st.plotly_chart(best_projected_lineup_bar,use_container_width=True,config = config) 
"#"

####  ROW 3 - ROSTER CHOICES / TABS  #### 
st.markdown(f"<center><h5>Active / Reserve Choices</center>",unsafe_allow_html=True) 
st.write("#")

team_tabs = st.tabs(list(team_abbrev_dict.keys()))

for tab, team_name in zip(team_tabs, team_abbrev_dict.values()):
        tab.plotly_chart(get_team_bar(rostered, team_name), use_container_width=True, config=config) 