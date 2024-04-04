import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
from utils import team_color
import streamlit_shadcn_ui as ui
from utils import stats_dict, team_color
import secrets

st.set_page_config(
    page_title="Season",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

config = {'displayModeBar': False}

st.cache_data()
def get_season_data():
    season_data = pd.read_excel("fantrax_season_data.xlsm")
    return season_data
df = get_season_data()

df['team'] = np.where(df['team'] == "Snead's Foot","Sneads Foot", df['team'])

# ###  PER TOURNAMENT AVERAGES  ###
st.write("#")
st.markdown("<center><h5>WEEKLY MEDIANS</h5></center>",unsafe_allow_html=True)
team_stat_medians = df.groupby('team')[['total_pts','cuts_made','total_holes','pp_hole','bird_num','eag_num','bog_num','dbog_num','plc_pts']].median()#.reset_index()
team_stat_medians.columns = 'Total Pts','Cuts Made','Holes Played','Pts/Hole','Birdies','Eagles','Bogeys','Doubles','Plc Pts'
team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']] = team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']].astype('int')
team_stat_medians = team_stat_medians.sort_values('Total Pts',ascending=False).round({'Cuts Made':1,'Pts/Hole':2,'Eagles':1,'Doubles':1})
st.dataframe(team_stat_medians,use_container_width=True)
##################

### SEASON TO DATE SCORE VS WEEKLY MEDIAN  ###
team_medians = pd.DataFrame(df.groupby('team',as_index=False)['median_delta'].sum()).sort_values(by='median_delta',ascending=False).reset_index(drop=True)
median_delta_bar = px.bar(team_medians,
                          text_auto='.3s',
                          color='team',
                          color_discrete_map=team_color,
                          template='plotly_dark',
                          labels={'index':'', 'value':''},
                          height=300,
                          title='season-to-date'
                         ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
                         ).update_yaxes(showticklabels=False,showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856'
                         ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),title_y=.75,title_x=.4,legend=dict(y=1.85, orientation='h',title='',font_color='#5A5856'))

### WEEKLY SCORE VS WEEKLY MEDIAN FOR EACH TEAM ###
team_weekly_deltas = pd.DataFrame(df[['team','week','median','median_delta']].groupby(['team','week'],as_index=False)[['median_delta','median']].sum())
wins_losses = df[['team','week','win_loss']]
wins_losses['win_loss'] = wins_losses['win_loss'].astype('bool')
team_weekly_deltas = team_weekly_deltas.merge(wins_losses, how='left', on=['team','week'])

newnames={'False':'Loss','True':'Win'}

median_delta_by_team_bar = px.bar(
    team_weekly_deltas.sort_values('median_delta',ascending=False),
    x='week',
    y='median_delta',
    color='win_loss',
    color_discrete_sequence=px.colors.qualitative.Safe, 
    facet_col='team',
    facet_col_wrap=2,
    facet_col_spacing=.1,
    facet_row_spacing=.16,
    height=1000,
    width=800,
    labels={'median_delta':'','week':''},
    template='plotly_dark',
    hover_name='week'
    # text_auto='.3s'
    ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),tickcolor='darkgrey', gridcolor='darkgrey'
    ).update_xaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),showticklabels=True,tickmode='array',tickvals = [1,2,3,4,5,6,7,8,9,10,11,12],ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer','PLAYERS','Valspar','Houston Open']
    ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,legend=dict(orientation='h',yanchor="bottom",y=1.1,xanchor="center",x=.5,title='',font_color='#5A5856')
    ).for_each_annotation(lambda a: a.update(text=a.text.replace("team=", ""))
    ).for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

### CUTS MADE DISTRIBUTION  ###
df['rounded_percentage'] = (df['cuts_made'] * 100).round().astype(int).astype(str) + '%'

cuts_made_hist1 = px.histogram(df.sort_values('cuts_made', ascending=False),
                              x='cuts_made',
                              template='plotly_dark',
                              labels={'cuts_made':'Players Thru Cut', 'count':''},
                              title="",
                              color_discrete_sequence=['grey'],
                              height=250,
                              text_auto='.0f'
                             )

cuts_made_hist1.update_layout(bargap=0.2, legend=dict(title="", x=.45, y=1.4, orientation='h'))
cuts_made_hist1.update_xaxes(tickvals = [1,2,3,4,5,6],
                            ticktext = ['1/6','2/6','3/6','4/6','5/6','6/6'],
                            showgrid=False,
                            tickfont=dict(
                                color='#5A5856'),
                                title_font=dict(
                                    color='#5A5856',
                                    size=14))
cuts_made_hist1.update_yaxes(showticklabels=False, showgrid=False, tickfont=dict(color='#5A5856'),
                             title_font_color='#5A5856', visible=False)

### CUTS MADE DISTRIBUTION  ###
newnames={'0':'Loss','1':'Win'}

cuts_made_hist = px.histogram(df.sort_values('cuts_made',ascending=False),
                    x='cuts_made',
                    text_auto='.2s',
                    # title='Win Percentage by Cuts Made',
                    template='plotly_dark',
                    labels={'cuts_made':'Players Thru Cut','count':''},
                    histfunc='count',
                    barnorm='percent',
                    barmode='stack',
                    color='win_loss',
#                     color_discrete_sequence=['red', 'green'],
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    height=250
                             ).update_layout(legend=dict(title="",x=.25,y=1.4,orientation='h',font_color='#5A5856'))

cuts_made_hist.update_layout(bargap=0.2)
cuts_made_hist.for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

cuts_made_hist.update_xaxes(tickvals = [1,2,3,4,5,6],
                            ticktext = ['1/6','2/6','3/6','4/6','5/6','6/6'],
                            showgrid=False,
                            tickfont=dict(
                                color='#5A5856'),
                                title_font=dict(
                                    color='#5A5856',
                                    size=14))

cuts_made_hist.update_yaxes(showticklabels=False, showgrid=False,visible= False)

st.markdown("##")
st.markdown("##")
col1,blank,col2 = st.columns([2,1,2])
with col1:
    st.markdown("<center><h5>Cuts Made Distribution</h5></center>",unsafe_allow_html=True)
    st.plotly_chart(cuts_made_hist1,use_container_width=True, config=config)
with col2:
    st.markdown("<center><h5>Win % by Cuts Made</h5></center>",unsafe_allow_html=True)
    st.plotly_chart(cuts_made_hist,use_container_width=True, config=config)

container = st.container(border=True)
with container:
    st.markdown('<center><h5>vs. WEEKLY MEDIAN SCORE</h5></center>',unsafe_allow_html=True)
    st.write("#")
    st.plotly_chart(median_delta_bar,config=config,use_container_width=True)
    with st.expander("CLICK HERE for team-by-team weekly"):
        st.plotly_chart(median_delta_by_team_bar,config=config, use_container_width=True)
##################

### WEEKLY BUBBLES WIN / LOSS  ###
newnames={'False':'Loss','True':'Win'}
temp_df = df.copy()
temp_df['win_loss'] = temp_df['win_loss'].astype('bool')
scatter_fig = px.scatter(temp_df,
                        x='week',
                        y='total_pts',
                        color='win_loss',
                        template='plotly_dark',
                        size='total_pts',
                        size_max=12,
                        hover_name=['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer','PLAYERS','Valspar','Houston Open']*8,
                        color_discrete_sequence=px.colors.qualitative.Pastel1,
                        labels={'week':'','total_pts':'Points Scored'},
                        custom_data=['team','cuts_made','players_started','win_loss','median_delta','total_pts','opponent']
                        ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,
                                        legend=dict(orientation='h',yanchor="bottom",y=1,xanchor="center",x=.5,title='',font_color='#5A5856')
                        ).update_xaxes(tickangle= -45,tickvals = [1,2,3,4,5,6,7,8,9,10,11,12],
                                       ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer','PLAYERS','Valspar','Houston Open'],
                                       tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14)
                        ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),tickcolor='darkgrey', gridcolor='darkgrey'
                        ).update_traces(marker=dict(size=15,opacity=.75,line=dict(width=1,color='darkslategrey'))
                        ).for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))


scatter_fig.update_traces(hovertemplate=
                    "<b>%{customdata[0]}</b> \
                    <br>%{customdata[3]}</b> \
                    <br>vs. %{customdata[6]}</b> \
                    <br> \
                    <br>Scored %{customdata[5]} Points</b> \
                    <br>%{customdata[4]} vs Median Score</b> \
                    <br> \
                    <br>%{customdata[1]}/%{customdata[2]} thru cut</b>")

st.markdown("##")
st.markdown("##")
st.markdown("<center><h5>WEEKLY SCORES</h5></center>",unsafe_allow_html=True)
st.plotly_chart(scatter_fig,use_container_width=True, config=config)

### FINISHING POSITION COMPARISON
finish_medians = round(df[['team','fin_1','fin_2','fin_3','fin_4','fin_5','fin_6']].groupby('team').median(),1).reset_index()
finish_medians.columns = 'Team','Best Finisher','2nd','3rd','4th','5th','Worst Finisher'
melted_finish_medians = finish_medians.melt(id_vars='Team',value_vars=['Best Finisher','2nd','3rd','4th','5th','Worst Finisher'])

fin_place_scatter = px.scatter(melted_finish_medians,
          x='variable',
          y='value',
          color='Team',
          color_discrete_map=team_color,
          template='plotly_white',
          labels={'value':'Finish Place<br>(log scale)','variable':''},
          log_y=True,
          height=600,
          ).update_traces(marker=dict(size=15,opacity=.75,line=dict(width=1,color='darkslategrey'))
          ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(font_color='#5A5856',title="")
          ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14)
          ).update_xaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14))

st.markdown("##")
st.markdown("##")
st.markdown("<center><h5>Median Finishing Place</h5></center>",unsafe_allow_html=True)
st.plotly_chart(fin_place_scatter,use_container_width=True, config=config)

corr_container = st.container(border=True)
with corr_container:

    col1,col2 = st.columns([1,2])
    with col1:
        "#"
        st.markdown(f"<center><h5>Which Stats<br>Correlate Most<br>with WINS?</h5></center>",unsafe_allow_html=True)
        "#"
        st.markdown(f"Choose a Statistic<br>",unsafe_allow_html=True)
        radio_options = [
            {"label": "Birdie to Bogey Ratio", "value": "bb_ratio", "id": "bb_ratio"},
            {"label": "Place Pts", "value": "plc_pts", "id": "plc_pts"},
            {"label": "Cuts Made", "value": "cuts_made", "id": "cuts_made"},
            {"label": "Points/Hole", "value": "pp_hole", "id": "pp_hole"},
            {"label": "Num of Pars", "value": "pars_num", "id": "pars_num"},
            {"label": "Num of Birdies", "value": "bird_num", "id": "bird_num"},
            {"label": "Num of Eagles", "value": "eag_num", "id": "eag_num"},
            {"label": "Num of Bogeys", "value": "bog_num", "id": "bog_num"},
            {"label": "Num of Dougle Bogeys", "value": "dbog_num", "id": "dbog_num"}
        ]
        radio_value = ui.radio_group(options=radio_options, default_value="bb_ratio", key="radio1")

    with col2:
        "#"
        r_squared = st.empty()
        df['bb_ratio'] = round(df.bird_num / df.bog_num,1)
        fig = px.scatter(df.groupby(['team'],as_index=False)[[radio_value,'win_loss']].sum(),
                    x=radio_value,
                    y='win_loss',
                    color='team',
                    color_discrete_map=team_color,
                    trendline='ols',trendline_scope='overall',trendline_color_override='black',
                    labels={'win_loss':'Wins',radio_value:stats_dict[radio_value]}
                ).update_traces(marker=dict(size=15,opacity=.75,line=dict(width=1,color='darkslategrey'))
                ).update_layout(showlegend=False#legend=dict(title=None,orientation='h',x=0,y=1.3))
                ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14), tickvals=[1,2,3,4,5,6,7,8,9,10,11,12]
                ).update_xaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14))

        results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
        r_squared.markdown(f"<h5><center>R-Squared: {results:.2f}</center></h5>", unsafe_allow_html=True)

        st.plotly_chart(fig,use_container_width=True, config=config)