import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import secrets

st.set_page_config(
    page_title="Fantrax Wk10",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
config = {'displayModeBar': False}


dg_key = st.secrets.dg_key

st.cache_data()
def get_projections():
    dg_proj = pd.read_csv(f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}")
    return dg_proj
dg_proj = get_projections()
dg_proj_copy = dg_proj.copy()

dg_proj = dg_proj[['player_name','proj_points_total']]
dg_proj.columns = ['player','proj_pts']

st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fx_wk10.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

teams.columns = ['player','team','active_reserve']
teams_dict = {'919':'Philly919','u_c':'unit_circle','NT 4':'New Team 4','NT 8':'Sneads Foot','txms':'txmoonshine','MG':'Team Gamble','grrr':'Putt Pirates','[AW]':'AlphaWired'}
teams['team'] = teams.team.map(teams_dict)
teams.set_index('player',inplace=True)

names = dg_proj['player'].str.split(expand=True)
names[0] = names[0].str.rstrip(",")
names[1] = names[1].str.rstrip(",")
names['player'] = names[1] + " " + names[0]

names['player'] = np.where(names['player']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
names['player'] = np.where(names['player']=='Si Kim', 'Si Woo Kim', names['player'])
names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])

dg_proj.set_index(names.player,inplace=True)

week = pd.merge(teams,dg_proj, left_index=True, right_index=True)#.reset_index()
week[['player','team','active_reserve']] = week[['player','team','active_reserve']].astype('string')
week.sort_values('proj_pts',ascending=False,inplace=True)

current_week = 10
num_players = len(week)

##  color dictionaries for teams and active/incactive
team_color={
                "Philly919": 'rgb(14,195,210)',
                "unit_circle": 'rgb(194,139,221)',
                "AlphaWired": 'rgb(247,160,93)',
                "Sneads Foot": 'rgb(70,214,113)',
                "New Team 4": 'rgb(247,94,56)',
                "Team Gamble": 'rgb(38,147,190)',
                "txmoonshine": 'rgb(219,197,48)',
                "Putt Pirates": 'rgb(115,112,106)'}

active_color={
    "Active":'rgb(146,146,143)',
    "Reserve":'rgb(220,222,202)'
    }

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

# BAR - ALL PLAYERS ACTIVE/RESERVE
fig1 = px.bar(week.drop(columns='player').sort_values(by = 'proj_pts',ascending=False).reset_index(),
       y = 'proj_pts',
       template='plotly_dark',
       hover_name = 'player',
       color = 'active_reserve',
       color_discrete_map=active_color,
       labels = {'_index':"", 'proj_pts':''},
       height=300,
       log_y=True,
       ).update_xaxes(showticklabels=False,
       ).update_yaxes(showgrid=False, tickvals=[50,60,70,80,90,100]
       ).update_layout(legend=dict(orientation='h',title='',y=1.2,x=.37)
       )

# BAR - ALL PLAYERS BY TEAM
fig2 = px.bar(week.sort_values(by='proj_pts',ascending=False).reset_index(drop=True),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':''},
    #   text_auto = ",.0f",
      template = 'plotly_dark',
      height=300,
      log_y=True,
      hover_name='player'
      ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False
                                                                 ).update_layout(legend=dict(y=1.2, orientation='h',title='')
                                                                                 )#.update_traces(texttemplate=week.player)

# BAR - TOP 6 PROJECTED PLAYERS BY TEAM
fig3 = px.bar(top_6_proj.set_index('player').sort_values(by = ['proj_pts','team'],ascending=False),
#           x = 'player',
          y = 'proj_pts',
          color='team',
          hover_name=top_6_proj.player,
          template='plotly_dark',
          labels = {'_index':" ",'player': '','proj_pts':''},
          height=300,
          color_discrete_map=team_color,
          log_y=True
          ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                   ).update_xaxes(showticklabels=False
                                                  ).update_yaxes(showgrid=False
                                                                 ).update_layout(legend=dict(y=1.5, orientation='h',title='')
                                                                                 )#.update_traces(texttemplate=week.player)

# BAR - HORIZONTAL ACTIVE ROSTERS
fig4 = px.bar(top_6_active.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
    y='team',
    x='proj_pts', 
    color='team', 
    template='plotly_dark',
    text_auto='.0s',
    title = "Current Rosters",
    labels = {'team': ' ', 'proj_pts':''},
    color_discrete_map=team_color,
    log_x=True,
    height=300
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)

# BAR - HORIZONTAL PROJECTED ROSTERS
fig5 = px.bar(top_6_proj.groupby('team',as_index=False)['proj_pts'].sum().sort_values(by='proj_pts',ascending=False),
    y = 'team',
    x = 'proj_pts',
    text_auto='.0s',
    color='team',
    template='plotly_dark',
    title = "Optimal Rosters",
    labels = {'team': ' ', 'proj_pts':''},
    color_discrete_map=team_color,
    height=300,
    log_x=True
    ).update_layout(showlegend=False, title_x=.33
                    ).update_xaxes(showticklabels=False)



###  MATCHKUPS ###
height = 250
# My Matchup
matchup = ['New Team 4','unit_circle']
fig6 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup))].drop(columns='player').sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':''},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_dark',
      hover_name='proj_pts',
      height=height,
    #   title=f"{matchup[0]} v {matchup[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100]).update_yaxes(gridcolor="#B1A999").update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33))

matchup2 = ['txmoonshine','Team Gamble']
fig7 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup2))].drop(columns='player').sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':''},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_dark',
      hover_name='proj_pts',
      height=height,
    #   title=f"{matchup2[0]} v {matchup2[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100]).update_yaxes(gridcolor="#B1A999").update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33))

# My Matchup
matchup3 = ['Putt Pirates','Philly919']
fig16 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup3))].drop(columns='player').sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':''},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_dark',
      hover_name='proj_pts',
      height=height,
    #   title=f"{matchup[0]} v {matchup[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100]).update_yaxes(gridcolor="#B1A999").update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33))

matchup4 = ['AlphaWired','Sneads Foot']
fig17 = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup4))].drop(columns='player').sort_values(by = 'proj_pts',ascending=False).reset_index(),
      y = 'proj_pts',
      color = 'team',
      color_discrete_map=team_color,
      labels = {'index':"", 'proj_pts':''},
#       text_auto = ",.0f",
      text='player',
      template = 'plotly_dark',
      hover_name='proj_pts',
      height=height,
    #   title=f"{matchup2[0]} v {matchup2[1]}",
      log_y=True).update_xaxes(showticklabels=False).update_yaxes(tickvals=[50,60,70,80,90,100]).update_yaxes(gridcolor="#B1A999").update_layout(legend=dict(orientation='h',title='',y=1.2,x=.33))


### makes individual team bars ###
def get_team_bar(team):
        fig = px.bar(week[week.team == team].sort_values(by='proj_pts',ascending=False), 
                                x = 'player', 
                                y = 'proj_pts', 
                                height=250,
                                color='active_reserve', 
                                text_auto='.2s',
                                template = 'plotly_dark',
                                color_discrete_map=active_color,
                                log_y=True,
                                labels = {'proj_pts':'','player':""}).update_yaxes(showticklabels=False,showgrid=False ).update_layout(legend=dict(orientation='h',title='',y=1.3,x=.33)).update_traces(width=.7)
        return fig


st.write("#")
### TITLE AND ROSTERS  ###
col1,col2,col3 = st.columns(3)

col1.markdown("###")
col1.markdown("###")
col1.markdown(f"<small>Fantrax Week {current_week}</small>",unsafe_allow_html=True)
col1.markdown("<h5>Players<br>Championship</h5>",unsafe_allow_html=True)
col1.markdown("###")
col1.markdown("###")
col1.markdown(f"{num_players} Rostered Players",unsafe_allow_html=True)
col2.plotly_chart(fig4,use_container_width=True,config = config)
col3.plotly_chart(fig5, use_container_width=True,config = config)


### WIDE BAR CHARTS  ###
tab1, tab2, tab3 = st.tabs(['by Proj Points', 'Sit / Start', 'Optimal'])
tab1.plotly_chart(fig2,use_container_width=True,config = config)
tab2.plotly_chart(fig1,use_container_width=True,config = config)
tab3.plotly_chart(fig3,use_container_width=True,config = config)


### MATCHUPS  ###
st.markdown("<center><h3>MATCHUPS</h3></center>",unsafe_allow_html=True)
col1,col2 = st.columns(2)

col1.plotly_chart(fig16,use_container_width=True,config = config)
col1.plotly_chart(fig17,use_container_width=True,config = config)

col2.plotly_chart(fig7,use_container_width=True,config = config)
col2.plotly_chart(fig6,use_container_width=True,config = config)

###  ACTIVE / RESERVE TABS  ###
st.markdown("<center><h3>ACTIVE/RESERVE</h3></center>",unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['919', 'u_c', 'txms','[AW]','NT4','MG','foot','grrr'])
tab1.plotly_chart(get_team_bar('Philly919'),use_container_width=True,config = config)
tab2.plotly_chart(get_team_bar('unit_circle'),use_container_width=True,config = config)
tab3.plotly_chart(get_team_bar('txmoonshine'),use_container_width=True,config = config)
tab4.plotly_chart(get_team_bar('AlphaWired'),use_container_width=True,config = config)
tab5.plotly_chart(get_team_bar('New Team 4'),use_container_width=True,config = config)
tab6.plotly_chart(get_team_bar('Team Gamble'),use_container_width=True,config = config)
tab7.plotly_chart(get_team_bar('Sneads Foot'),use_container_width=True,config = config)
tab8.plotly_chart(get_team_bar('Putt Pirates'),use_container_width=True,config = config)


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
    
# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)



    