import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
from utils import get_team_bar, get_all_player_bar, get_matchup_bar, fix_long_names, teams_dict, team_color, active_color
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

df = pd.read_excel(r"C:\Users\mikej\Desktop\fantrax_season_data.xlsm")

### SEASON TO DATE SCORE VS WEEKLY MEDIAN  ###
team_medians = pd.DataFrame(df.groupby('team',as_index=False)['median_delta'].sum()).sort_values(by='median_delta',ascending=False).reset_index(drop=True)
median_delta_bar = px.bar(team_medians,
                          text_auto='.2s',
                          color='team',
                          color_discrete_map=team_color,
                          template='plotly_dark',
                          labels={'index':'', 'value':''},
                          height=300
                         )

median_delta_bar.update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856'))
median_delta_bar.update_yaxes(showticklabels=False, showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856')
median_delta_bar.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(y=1.75, orientation='h',title='',font_color='#5A5856'))
st.markdown("<center><h5>vs. WEEKLY MEDIAN</h5></center>",unsafe_allow_html=True)
st.plotly_chart(median_delta_bar,use_container_width=True)
##################

# ###  PER TOURNAMENT AVERAGES  ###
st.markdown("<center><h5>WEEKLY PROFILE</h5></center>",unsafe_allow_html=True)
team_stat_medians = df.groupby('team')[['total_pts','cuts_made','total_holes','pp_hole','bird_num','eag_num','bog_num','dbog_num','plc_pts']].mean()#.reset_index()
team_stat_medians.columns = 'Total Pts','Cuts Made','Holes Played','Pts/Hole','Birdies','Eagles','Bogeys','Doubles','Plc Pts'
team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']] = team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']].astype('int')
team_stat_medians = team_stat_medians.sort_values('Total Pts',ascending=False).round({'Cuts Made':1,'Pts/Hole':2,'Eagles':1,'Doubles':1})
st.dataframe(team_stat_medians,use_container_width=True)
##################


### WEEKLY BUBBLES WIN / LOSS  ###

temp_df = df.copy()
temp_df['win_loss'] = temp_df['win_loss'].astype('bool')
scatter_fig = px.scatter(temp_df,
                        x='week',
                        y='total_pts',
                        color='win_loss',
                        # height=800,
                        width=600,
                        template='plotly_dark',
                        size='cuts_made',
                        size_max=14,
                        hover_name='team',
                        color_discrete_sequence=px.colors.qualitative.Pastel1,
                        labels={'week':'','total_pts':'Points Scored'}
                        ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,
                                        legend=dict(orientation='h',yanchor="bottom",y=1,xanchor="center",x=.5,title='')
                        ).update_xaxes(tickangle= -45,tickvals = [1,2,3,4,5,6,7,8,9],
                                       ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer']
                        ).update_traces(marker=dict(line_color='black',opacity=.8))

st.plotly_chart(scatter_fig,use_container_width=True, config=config)

### CUTS MADE DISTRIBUTION  ###
cuts_made_hist = px.histogram(df,
                    x='cuts_made',
                    text_auto=True,
                    template='plotly_dark',
                    labels={'cuts_made':'','count':''},
                    color='win_loss',
                    histfunc='count'
                             )

cuts_made_hist.update_xaxes(tickvals = [2,3,4,5,6],
                            ticktext = ['2/6','3/6','4/6','5/6','6/6'])

cuts_made_hist.update_yaxes(showticklabels=False, showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856',visible= False)
st.markdown("<center><h5>Cuts Made Distribution</h5></center>",unsafe_allow_html=True)
st.plotly_chart(cuts_made_hist,use_container_width=True, config=config)

### FINISHING POSITION COMPARISON
finish_medians = round(df[['team','fin_1','fin_2','fin_3','fin_4','fin_5','fin_6']].groupby('team').median(),1).reset_index()
finish_medians.columns = 'Team','Top Finisher','2nd','3rd','4th','5th','Worst Finisher'
melted_finish_medians = finish_medians.melt(id_vars='Team',value_vars=['Top Finisher','2nd','3rd','4th','5th','Worst Finisher'])

fin_place_scatter = px.scatter(melted_finish_medians,
          x='variable',
          y='value',
          color='Team',
          color_discrete_map=team_color,
          template='plotly_white',
          labels={'value':'Median Finish','variable':''},
          ).update_traces(marker_size=12
          ).update_layout(legend=dict(title=None,orientation='h',x=0,y=1.3))

st.plotly_chart(fin_place_scatter,use_container_width=True)

### CORRELATION TO WINS BY STAT - SCATTER PLOTS WITH SLIDER / TOGGLE / RADIO BUTTON FOR EACH STAT


stats_to_compare = ['pars_num','bird_num','eag_num','bog_num','dbog_num','plc_pts','cuts_made','median_delta','pp_hole']

for stat in stats_to_compare:
    scatter_df = df.groupby(['team'],as_index=False)[[stat,'win_loss']].mean()
    fig = px.scatter(scatter_df,
              x=stat,
              y='win_loss',
              color='team',
              color_discrete_map=team_color,
              trendline='ols',trendline_scope='overall',trendline_color_override='black',
          ).update_traces(marker_size=12
          ).update_layout(legend=dict(title=None,orientation='h',x=0,y=1.3))
    results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared

st.markdown(f"Comparing {stat} with Wins<br>R-Squared: {results:.2f}",unsafe_allow_html=True)
st.plotly_chart(fig,use_container_width=True)