import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="PGA Pressure",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.cache_data()
def get_projections():
    dg_proj = pd.read_csv(r"proj_wk7.csv")#,usecols=['dk_name','total_points'])
    return dg_proj
dg_proj = get_projections()
dg_proj_copy = dg_proj.copy()
dg_proj = dg_proj[['dk_name','total_points']]

st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fx_wk7.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

teams.columns = ['player','team','active_reserve']
teams_dict = {'919':'Philly919','u_c':'unit_circle','NT 4':'Sneads Shoe','NT 8':'New Team 8','txms':'txmoonshine','MG':'Team Gamble','GRR':'Putt Pirates','[AW]':'AlphaWired'}
teams['team'] = teams.team.map(teams_dict)
teams.set_index('player',inplace=True)

dg_proj.columns = ['player','proj_pts']
dg_proj.set_index('player',inplace=True)

week = pd.merge(teams,dg_proj, left_index=True, right_index=True).reset_index()
week[['player','team','active_reserve']] = week[['player','team','active_reserve']].astype('string')

##  color dictionaries for teams and active/incactive

team_color={
                "Philly919": 'rgb(127,60,141)',
                "unit_cirle": 'rgb(17,165,121)',
                "AlphaWired": 'rgb(57,105,172)',
                "Sneads Shoe": 'rgb(242,183,1)',
                "New Team 8": 'rgb(231,63,116)',
                "Team Gamble": 'rgb(230,131,16)',
                "txmoonshine": 'rgb(0,134,139)',
                "Putt Pirates": 'rgb(165,170,153)'}

active_color={"Active":'rgb(93,105,177)',"Reserve":'rgb(218,165,27)'}

# TOP PROJ PLAYERS
top_6_proj = pd.DataFrame()
for team in week.team.unique():
    temp = week[week.team==team][['team','player','proj_pts','active_reserve']].sort_values(by='proj_pts',ascending=False)[:6]
    top_6_proj = pd.concat([top_6_proj,temp])
    top_6_proj = top_6_proj.sort_values('proj_pts',ascending=False).reset_index(drop=True)

# TOP ACTIVE PLAYERS
top_6_active = pd.DataFrame()
for team in week.team.unique():
    temp = week[(week.team==team) & (week.active_reserve=='Active')][['team','player','proj_pts','active_reserve']]#.sort_values(by=['active_reserve','proj_pts'],ascending=False)[:6]
    top_6_active = pd.concat([top_6_active,temp])

# NEEDED METRICS
mean_starter = top_6_proj.proj_pts.mean().round(1)
median_starter = round(top_6_proj.proj_pts.median(),1)

# BAR - ALL PLAYERS ACTIVE/RESERVE
fig1 = px.bar(week.sort_values(by = 'proj_pts',ascending=False).reset_index(),
       y = 'proj_pts',
       template='plotly_white',
       hover_name = 'player',
       color = 'active_reserve',
       color_discrete_map=active_color,
       labels = {'_index':"", 'proj_pts':'Projected Pts'},
       height=400,
       log_y=True
       ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False)

# BAR - ALL PLAYERS BY TEAM
fig2 = px.bar(week.sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
      text_auto = ",.0f",
      template = 'plotly_white',
      height=400,
      log_y=True,
      title='All Mexico Open Players on Rosters',
      hover_name='player'
      ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_layout(title_x=.25
                                                                  ).update_yaxes(showgrid=False)

# BAR - TOP 6 PROJECTED PLAYERS BY TEAM
fig3 = px.bar(top_6_proj.set_index('player').sort_values(by = ['proj_pts','team'],ascending=False),
#           x = 'player',
          y = 'proj_pts',
          color='team',
          hover_name=top_6_proj.player,
          template='plotly_white',
          labels = {'_index':" ",'player': '','proj_pts':'Projected Pts'},
          title = f"<b>Mean: {mean_starter}</b>",
          text_auto=True,
          height=400,
          color_discrete_map=team_color
          ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_layout(title_x=.25
                                                                  ).update_yaxes(showgrid=False)

# BAR - HORIZONTAL ACTIVE ROSTERS
fig4 = px.bar(top_6_active.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
    y='team',
    x='proj_pts', 
    color='team', 
    template='plotly_white',
    text_auto=True,
    title = "Current Roster",
    labels = {'team': ' ', 'proj_pts':''},
    color_discrete_map=team_color,
    log_x=True
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)

# BAR - HORIZONTAL PROJECTED ROSTERS
fig5 = px.bar(top_6_proj.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
    y = 'team',
    x = 'proj_pts',
    text_auto=True,
    color='team',
    template='plotly_white',
    title = "Optimal Roster",
    labels = {'team': ' ', 'proj_pts':''},
    color_discrete_map=team_color,
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)

# My Matchup
matchup = ['txmoonshine','unit_circle']
fig6 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_white',
      hover_name='proj_pts',
      title=f"{matchup[0]} v {matchup[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100])

matchup = ['Sneads Shoe','Philly919']
fig7 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
      text='player',
      template = 'plotly_white',
      hover_name='proj_pts',
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100])

st.markdown("<h1>Fantrax Wk7 - The Mexico Open</h1>")
"---"
col1, blank, col2 = st.columns([2,1,2])
with col1:
    st.plotly_chart(fig4,use_container_width=True)
with blank:
    st.markdown("##")
with col2:  
    st.plotly_chart(fig5, use_container_width=True)

st.subheader("All Mexico Open Players on Rosters")
st.plotly_chart(fig1,use_container_width=True)

st.subheader("Optimal Player Projections")
tab1, tab2 = st.tabs(['by Team', 'by Points'])
with tab1:
    st.plotly_chart(fig3,use_container_width=True)
with tab2:
    st.plotly_chart(fig2,use_container_width=True)

st.subheader("Our Matchups")
tab1, tab2 = st.tabs(['Phil', 'Mike'])
with tab1:
    st.plotly_chart(fig7,use_container_width=True)
with tab2:
    st.plotly_chart(fig6,use_container_width=True)

dg_proj_copy = round(dg_proj_copy[['dk_name','dk_salary','early_late_wave','total_points','value','projected_ownership']],2).sort_values(by='dk_salary',ascending=False).reset_index(drop=True)
st.dataframe(dg_proj_copy,use_container_width=True)



    