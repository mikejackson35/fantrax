import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Fantrax Wk9",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
config = {'displayModeBar': False}

# st.markdown("""
# <style>
            
# # [data-testid="stAppViewContainer"] {
# #     padding: 0px 400px 0px 400px;
# # }
            
# [data-testid="stElementToolbar"] {
#     display: none;
# }
            
# .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
# font-size:1rem;
# }
            
# [data-baseweb="tab-list"] {
#     gap: 4px;
# }

# [data-baseweb="tab"] {
#     height: 30px;
#     width: 500px;
#     white-space: pre-wrap;
#     background-color: #A29F99;
#     # background-color: #E8E6E3;
#     border-radius: 4px 4px 0px 0px;
#     gap: 1px;
#     padding-top: 8px;
#     padding-bottom: 8px;
# }
            
# </style>
#         """, unsafe_allow_html=True)

st.cache_data()
def get_projections():
    dg_proj = pd.read_csv(r"proj_wk9.csv")#,usecols=['dk_name','total_points'])
    return dg_proj
dg_proj = get_projections()
dg_proj_copy = dg_proj.copy()
dg_proj = dg_proj[['dk_name','total_points']]

st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fx_wk9.csv",usecols=['Player','Status','Roster Status'])
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

### opponent inputs ###
mike_opp = 'AlphaWired'
phil_opp = 'txmoonshine'
current_week = 9

# TOP PROJ PLAYERS
top_6_proj = pd.DataFrame()
for team in week.team.unique():
    temp = week[week.team==team][['team','player','proj_pts','active_reserve']].sort_values(by='proj_pts',ascending=False)[:6]
    top_6_proj = pd.concat([top_6_proj,temp])
    top_6_proj = top_6_proj.sort_values('proj_pts',ascending=False).reset_index(drop=True)

# ACTIVE PLAYERS BY TEAM
top_6_active = pd.DataFrame()
for team in week.team.unique():
    temp = week[(week.team==team) & (week.active_reserve=='Active')][['team','player','proj_pts','active_reserve']]
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
       height=300,
       log_y=True,
       title=f"Avg Proj Pts {mean_starter}"
       ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey',line_width=.5,
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False, tickvals=[50,60,70,80,90,100]
                                                                 ).update_layout(title_x=.4,legend=dict(orientation='h',title='',y=1.2,x=.33))

# BAR - ALL PLAYERS BY TEAM
fig2 = px.bar(week.sort_values(by='proj_pts',ascending=False).reset_index(drop=True),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':'Projected Pts'},
      text_auto = ",.0f",
      template = 'plotly_white',
      height=300,
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
          height=300,
          color_discrete_map=team_color,
          log_y=True
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
    height=350
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
    height=350,
    log_x=True
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)

# My Matchup
matchup = [mike_opp,'unit_circle']
fig6 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_white',
      hover_name='proj_pts',
      height=300,
    #   title=f"{matchup[0]} v {matchup[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100]).update_yaxes(gridcolor="#B1A999").update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33))

matchup2 = [phil_opp,'Philly919']
fig7 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup2))].sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'_index':"", 'proj_pts':'Projected Pts'},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_white',
      hover_name='proj_pts',
      height=300,
    #   title=f"{matchup2[0]} v {matchup2[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100]).update_yaxes(gridcolor="#B1A999").update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33))

height = 250
# PHILLY919
fig8 = px.bar(week[week.team == 'Philly919'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# unit_circle
fig9 = px.bar(week[week.team == 'unit_circle'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# PHIL OPPONENT CHOICES
fig10 = px.bar(week[week.team == 'txmoonshine'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# MIKE CHOICES
fig11 = px.bar(week[week.team == 'AlphaWired'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# PHIL CHOICES
fig12 = px.bar(week[week.team == 'New Team 4'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# MIKE CHOICES
fig13 = px.bar(week[week.team == 'Team Gamble'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# PHIL OPPONENT CHOICES
fig14 = px.bar(week[week.team == 'Sneads Shoe'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)

# MIKE CHOICES
fig15 = px.bar(week[week.team == 'Putt Pirates'].sort_values(by='proj_pts',ascending=False), 
                x = 'player', 
                y = 'proj_pts', 
                height=height,
                color='active_reserve', 
                text_auto=True,
                template = 'plotly_dark',
                color_discrete_map=active_color,
                log_y=True,
                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False ).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33)).update_traces(width=.7)


st.write("#")
st.markdown(f"<center>Fantrax Week {current_week}</center>",unsafe_allow_html=True)
st.markdown("<center><h2>The Arnold Palmer Invitational</h2></center>",unsafe_allow_html=True)
"---"
st.markdown(f"<center><h5>WHO IS BEING USED?</h5></center>",unsafe_allow_html=True)
num_players = len(week)
st.markdown(f"<center>of the {num_players} Rostered Players</center>",unsafe_allow_html=True)
st.plotly_chart(fig1,use_container_width=True,config = config)
"---"
st.markdown("<center><h5>PROJECTED POINTS</h5></center>",unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['919', 'u_c', 'txms','[AW]','NT4','MG','foot','grrr'])
with tab1:
    st.plotly_chart(fig8,use_container_width=True,config = config)
with tab2:
    st.plotly_chart(fig9,use_container_width=True,config = config)
with tab3:
    st.plotly_chart(fig10,use_container_width=True,config = config)
with tab4:
    st.plotly_chart(fig11,use_container_width=True,config = config)
with tab5:
    st.plotly_chart(fig12,use_container_width=True,config = config)
with tab6:
    st.plotly_chart(fig13,use_container_width=True,config = config)
with tab7:
    st.plotly_chart(fig14,use_container_width=True,config = config)
with tab8:
    st.plotly_chart(fig15,use_container_width=True,config = config)
"---"
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig4,use_container_width=True,config = config)
with col2:  
    st.plotly_chart(fig5, use_container_width=True,config = config)
"---"
st.markdown("<center><h5>OPTIMAL PROJECTIONS</h5></center>",unsafe_allow_html=True)

tab1, tab2 = st.tabs(['Top 6 by Team', 'All Available by Proj Points'])
with tab1:
    st.plotly_chart(fig3,use_container_width=True,config = config)
with tab2:
    st.plotly_chart(fig2,use_container_width=True,config = config)

st.markdown("<center><h5>MATCHUPS</h5></center>",unsafe_allow_html=True)
tab1, tab2 = st.tabs(['Phil', 'Mike'])
with tab1:
    st.plotly_chart(fig7,use_container_width=True,config = config)
with tab2:
    st.plotly_chart(fig6,use_container_width=True,config = config)


# st.markdown("##")
# st.markdown("<center><h5>DRAFT KINGS PROJECTIONS</h5></center>",unsafe_allow_html=True)

# dg_proj_copy = pd.DataFrame(round(dg_proj_copy[['dk_name','dk_salary','total_points','value','projected_ownership']],2)).sort_values(by='dk_salary',ascending=False).reset_index(drop=True)
# st.dataframe(dg_proj_copy.round(2).style.background_gradient(subset=['value'],cmap='Greys').format(precision=2),
#              hide_index=True,
#              height=1000,
#              column_config={
#                   'dk_name':'Name',
#                   'dk_salary': st.column_config.NumberColumn(
#                        'DK Salary',
#                        format = "$ %.0f"
#                     ),
#                 #    'early_late_wave':'Early/Late Wave',
#                    'total_points':'Proj Pts',
#                    'value': 'Value',
#                    'projected_ownership':'pOwn',
#                    'adj_from_baseline': 'Baseline Adj'
#              },
#              use_container_width=True
#         )



    