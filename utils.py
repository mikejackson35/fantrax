import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

def get_team_bar(week,team):
        fig = px.bar(week[week.team == team].sort_values(by='proj_pts',ascending=False), 
                                x = 'player', 
                                y = 'proj_pts', 
                                height=250,
                                color='active_reserve', 
                                text_auto='.2s',
                                template = 'plotly_dark',
                                color_discrete_map=active_color,
                                log_y=True,
                                labels = {'proj_pts':'','player':""}
                                ).update_yaxes(showticklabels=False,showgrid=False, tickfont=dict(color='#5A5856')
                                ).update_xaxes(tickfont=dict(color='#5A5856')
                                ).update_layout(legend=dict(orientation='h',title='',y=1.3,x=.33)
                                ).update_traces(width=.7)
        return fig

def get_all_player_bar(week,color_by,color_map):
        all_player_bar = px.bar(week.sort_values(by='proj_pts',ascending=False).reset_index(drop=True),
                                y = 'proj_pts',
                                template='plotly_dark',
                                color = color_by,
                                color_discrete_map=color_map,
                                labels = {'index':"", 'proj_pts':''},
                                height=300,
                                log_y=True,
                                hover_name='player'
                                ).add_hline(y=week.proj_pts.mean(),line_color='darkslategrey'
                                ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
                                ).update_yaxes(showgrid=False,tickfont=dict(color='#5A5856')
                                ).update_layout(legend=dict(y=1.5, orientation='h',title='',font_color='#5A5856'))
        return all_player_bar

def get_matchup_bar(week,matchup):
        matchup_bar = px.bar(week[(week.active_reserve=='Active') & (week.team.isin(matchup))].drop(columns='player').sort_values(by = 'proj_pts',ascending=False).reset_index(),
                             y = 'proj_pts',
                             color = 'team',
                             color_discrete_map=team_color,
                             labels = {'index':"", 'proj_pts':''},
                             text='player',
                             template = 'plotly_dark',
                             hover_name='proj_pts',
                             height=250,
                             log_y=True
                             ).update_xaxes(showticklabels=False
                             ).update_yaxes(tickvals=[50,60,70,80,90,100], tickfont=dict(color='#5A5856')
                             ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856')
                             ).update_layout(legend=dict(orientation='h',title='',y=1.25,x=.2,font_color='#5A5856'))
        return matchup_bar

def fix_long_names(dg_proj):
        names = dg_proj['player'].str.split(expand=True)                  
        names[0] = names[0].str.rstrip(",")
        names[1] = names[1].str.rstrip(",")
        names['player'] = names[1] + " " + names[0]

        names['player'] = np.where(names['player']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
        names['player'] = np.where(names['player']=='Si Kim', 'Si Woo Kim', names['player'])
        names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
        names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
        names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
        names['player'] = np.where(names['player']=='Vince Whaley', 'Vincent Whaley', names['player'])
        names['player'] = np.where(names['player']=='kevin Yu', 'Kevin Yu', names['player'])
        return names

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

teams_dict = {'919':'Philly919','u_c':'unit_circle',
              'NT 4':'New Team 4','NT 8':'Sneads Foot',
              'txms':'txmoonshine','MG':'Team Gamble',
              'grrr':'Putt Pirates','[AW]':'AlphaWired'}