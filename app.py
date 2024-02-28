import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Pip/Jacko",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.cache_data()
def get_projections():
    dg_proj = pd.read_csv(r"proj_wk8.csv")#,usecols=['dk_name','total_points'])
    return dg_proj
dg_proj = get_projections()
dg_proj_copy = dg_proj.copy()
dg_proj = dg_proj[['dk_name','total_points']]

st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fx_wk8.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

teams.columns = ['player','team','active_reserve']
teams_dict = {'919':'Philly919','u_c':'unit_circle','NT 4':'New Team 4','NT 8':'Sneads Shoe','txms':'txmoonshine','MG':'Team Gamble','grrr':'Putt Pirates','[AW]':'AlphaWired'}
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
                "New Team 4": 'rgb(231,63,116)',
                "Team Gamble": 'rgb(230,131,16)',
                "txmoonshine": 'rgb(0,134,139)',
                "Putt Pirates": 'rgb(165,170,153)'}

active_color={"Active":'rgb(146,146,143)',"Reserve":'rgb(220,222,202)'}

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
       height=350,
       log_y=True
       ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False, tickvals=[50,60,70,80,90,100])

# BAR - ALL PLAYERS BY TEAM
fig2 = px.bar(week.sort_values(by='proj_pts',ascending=False).reset_index(drop=True),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':'Projected Pts'},
      text_auto = ",.0f",
      template = 'plotly_white',
      height=350,
      log_y=True,
      hover_name='player'
      ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False
                                                                 ).update_layout(legend=dict(y=1.5, orientation='h'))

# BAR - TOP 6 PROJECTED PLAYERS BY TEAM
fig3 = px.bar(top_6_proj.set_index('player').sort_values(by = ['proj_pts','team'],ascending=False),
#           x = 'player',
          y = 'proj_pts',
          color='team',
          hover_name=top_6_proj.player,
          template='plotly_white',
          labels = {'_index':" ",'player': '','proj_pts':'Projected Pts'},
          text_auto=True,
          height=350,
          color_discrete_map=team_color
          ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False
                                                                 ).update_layout(legend=dict(y=1.5, orientation='h'))

# BAR - HORIZONTAL ACTIVE ROSTERS
fig4 = px.bar(top_6_active.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
    y='team',
    x='proj_pts', 
    color='team', 
    template='plotly_white',
    text_auto=True,
    title = "Current Rosters",
    labels = {'team': ' ', 'proj_pts':''},
    color_discrete_map=team_color,
    log_x=True,
    height=400
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)

# BAR - HORIZONTAL PROJECTED ROSTERS
fig5 = px.bar(top_6_proj.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
    y = 'team',
    x = 'proj_pts',
    text_auto=True,
    color='team',
    template='plotly_white',
    title = "Optimal Rosters",
    labels = {'team': ' ', 'proj_pts':''},
    color_discrete_map=team_color,
    height=400,
    log_x=True
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)

# My Matchup
matchup = ['Team Gamble','unit_circle']
fig6 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_white',
      hover_name='proj_pts',
      height=350,
      title=f"{matchup[0]} v {matchup[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100])

matchup2 = ['New Team 4','Philly919']
fig7 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup2))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_white',
      hover_name='proj_pts',
      height=350,
      title=f"{matchup2[0]} v {matchup2[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100])

st.write("#")
st.markdown("Fantrax Week 8")
st.header("Cognizant Classic in The Palm Beaches")
"---"
col1, col2, blank = st.columns([2,2,1])
with col1:
    st.plotly_chart(fig4,use_container_width=True)
with blank:
    st.markdown("##")
with col2:  
    st.plotly_chart(fig5, use_container_width=True)

num_players = len(week)

st.markdown(f"<h5>Start/Sit by Projected Pts - {num_players} Players</h5>",unsafe_allow_html=True)
st.plotly_chart(fig1,use_container_width=True)

st.markdown("<h5>Optimal Player Projections</h5>",unsafe_allow_html=True)
st.markdown(f"Mean: {mean_starter}",unsafe_allow_html=True)
tab1, tab2 = st.tabs(['by Team', 'by Points'])
with tab1:
    st.plotly_chart(fig3,use_container_width=True)
with tab2:
    st.plotly_chart(fig2,use_container_width=True)

st.markdown("<h5>Our Matchups</h5>",unsafe_allow_html=True)
tab1, tab2 = st.tabs(['Phil', 'Mike'])
with tab1:
    st.plotly_chart(fig7,use_container_width=True)
with tab2:
    st.plotly_chart(fig6,use_container_width=True)

st.markdown("<h5>Draft Kings Projections</h5>",unsafe_allow_html=True)

dg_proj_copy = pd.DataFrame(round(dg_proj_copy[['dk_name','dk_salary','early_late_wave','total_points','value','projected_ownership']],2)).sort_values(by='dk_salary',ascending=False).reset_index(drop=True)
st.dataframe(dg_proj_copy.round(2).style.background_gradient(subset=['value'],cmap='Greys').format(precision=2),
             hide_index=True,
             column_config={
                  'dk_name':'Name',
                  'dk_salary': st.column_config.NumberColumn(
                       'DK Salary',
                       format = "$ %.0f"
                    ),
                   'early_late_wave':'Early/Late Wave',
                   'total_points':'Proj Pts',
                   'value': 'Value',
                   'projected_ownership':'pOwn'
             },
             use_container_width=True
        )



    