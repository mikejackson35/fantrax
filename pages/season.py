import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
import streamlit_shadcn_ui as ui
from dict_utils import *
from constants import *

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
    season_data = pd.read_excel(r"fantrax_season_data.xlsm")
    return season_data
df = get_season_data()

st.write("#")
##  STANDINGS  ##
st.markdown("<center><h5>STANDINGS</h5></center>",unsafe_allow_html=True)
standings = df.groupby('team')[['win_loss','total_pts']].sum().sort_values('win_loss',ascending=False)
standings['loss'] = (WEEK_NUMBER - 1) - standings['win_loss']
standings.columns = ['Win','Points','Loss']
standings = standings[['Win','Loss','Points']]

st.dataframe(standings,use_container_width=True)
st.markdown("##")

# ###  PER TOURNAMENT AVERAGES  ###
# st.write("#")
st.markdown("<center><h5>WEEKLY SCORING</h5></center>",unsafe_allow_html=True)
team_stat_avgs = df.groupby('team')[['total_pts','cuts_made','total_holes','pp_hole','bird_num','eag_num','bog_num','dbog_num','plc_pts']].mean()
team_stat_avgs.columns = 'Total Pts','Cuts Made','Holes Played','Pts/Hole','Birdies','Eagles','Bogeys','Doubles','Plc Pts'
team_stat_avgs[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']] = team_stat_avgs[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']].astype('int')
team_stat_avgs.index.name = 'Team'
team_stat_avgs = team_stat_avgs.sort_values('Total Pts',ascending=False).round({'Cuts Made':1,'Pts/Hole':2,'Eagles':1,'Doubles':1})

team_stat_medians = df.groupby('team')[['total_pts','cuts_made','total_holes','pp_hole','bird_num','eag_num','bog_num','dbog_num','plc_pts']].median()
team_stat_medians.columns = 'Total Pts','Cuts Made','Holes Played','Pts/Hole','Birdies','Eagles','Bogeys','Doubles','Plc Pts'
team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']] = team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']].astype('int')
team_stat_medians.index.name = 'Team'
team_stat_medians = team_stat_medians.sort_values('Total Pts',ascending=False).round({'Cuts Made':1,'Pts/Hole':2,'Eagles':1,'Doubles':1})

tab1,tab2 = st.tabs(['Averages','Medians'])
with tab1:
    st.dataframe(team_stat_avgs,use_container_width=True)
with tab2:
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
                          height=350,
                          title='Season to Date'
                         ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
                         ).update_yaxes(showticklabels=False,showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856'
                         ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),title_y=.75,title_x=.4, legend=dict(y=1.85, orientation='h',title='',font_color='#5A5856')
                         ).update_traces(textfont_size=12, textfont_family='Arial Black',width=.7)

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
    facet_col_wrap=1,
    # facet_col_spacing=.1,
    # facet_row_spacing=.16,
    height=3000,
    # width=800,
    labels={'median_delta':'','week':''},
    template='plotly_dark',
    hover_name='week',
    text_auto='.0f'
    ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),tickcolor='darkgrey', gridcolor='darkgrey'
    ).update_xaxes(tickfont=dict(color='#5A5856', size=11),title_font=dict(color='#5A5856',size=14),showticklabels=True,tickmode='array',tickvals = tickvals,ticktext = ticktext
    ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,legend=dict(orientation='h',yanchor="bottom",y=1.1,xanchor="center",x=.5,title='',font_color='#5A5856')
    ).for_each_annotation(lambda a: a.update(text=a.text.replace("team=", ""))
    ).for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name]))
    ).update_traces(textfont_family='Arial Black',width=.75)

# Update facet titles to be larger and bold
for annotation in median_delta_by_team_bar.layout.annotations:
    annotation.update(font=dict(size=20, family='Arial Black'))



### CUTS MADE DISTRIBUTION  ###
cuts_made_hist1 = px.histogram(df[~df.week.isin(no_cut_weeks)].sort_values('cuts_made', ascending=False),
                              x='cuts_made',
                              template='plotly_dark',
                              labels={'cuts_made':'Players Thru Cut', 'count':''},
                              title="Distribution Cuts Made",
                              color_discrete_sequence=['#5A5856'],
                              height=275,
                              text_auto='.0f'
                             )

cuts_made_hist1.update_layout(bargap=0.2, legend=dict(title="", x=.45, y=1.3, orientation='h'),title_x=.25)
cuts_made_hist1.update_xaxes(tickvals = [1,2,3,4,5,6],
                            ticktext = ['1/6','2/6','3/6','4/6','5/6','6/6'],
                            showgrid=False,
                            tickfont=dict(
                                color='#000000'),
                                title_font=dict(
                                    color='#5A5856',
                                    size=14))
cuts_made_hist1.update_yaxes(showticklabels=False, showgrid=False, tickfont=dict(color='#5A5856'),
                             title_font_color='#5A5856', visible=False)

### CUTS MADE DISTRIBUTION  ###
newnames={'0':'Loss','1':'Win'}

cuts_made_hist = px.histogram(df[~df.week.isin(no_cut_weeks)].sort_values('cuts_made', ascending=False),
                    x='cuts_made',
                    text_auto='.2s',
                    title='Win % by Cuts Made',
                    template='plotly_dark',
                    labels={'cuts_made':'Players Thru Cut','count':''},
                    histfunc='count',
                    barnorm='percent',
                    barmode='stack',
                    color='win_loss',
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    height=275)

cuts_made_hist.update_layout(legend=dict(title="",x=.25,y=1.4,orientation='h',font_color='#5A5856'),title_x=.25,bargap=0.2)
cuts_made_hist.for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

cuts_made_hist.update_xaxes(tickvals = [1,2,3,4,5,6],
                            ticktext = ['1/6','2/6','3/6','4/6','5/6','6/6'],
                            showgrid=False,
                            tickfont=dict(
                                color='#000000'),
                                title_font=dict(
                                    color='#5A5856',
                                    size=14))

cuts_made_hist.update_yaxes(showticklabels=False, showgrid=False,visible= False)

st.markdown("##")
st.markdown("##")
col1,blank,col2 = st.columns([1.9,1.2,1.9])
with col1:
    st.plotly_chart(cuts_made_hist1,use_container_width=True, config=config)
with blank:
    st.markdown("#")
    # st.markdown("#")
    st.markdown("<center><small>*no cut events<br> excluded",unsafe_allow_html=True)
with col2:
    st.plotly_chart(cuts_made_hist,use_container_width=True, config=config)

container = st.container(border=True)
with container:
    st.markdown('<center><h5>vs. WEEKLY MEDIAN SCORE</h5></center>',unsafe_allow_html=True)
    st.plotly_chart(median_delta_bar,config=config,use_container_width=True)
    with st.expander("EXPAND for team by team"):
        st.plotly_chart(median_delta_by_team_bar,config=config, use_container_width=True)
##################

### WEEKLY BUBBLES WIN / LOSS  ###
st.write("#")
weekly_bubble_container = st.container(border=True)

temp_df = df.copy()
temp_df['win_loss'] = temp_df['win_loss'].astype('bool')

with weekly_bubble_container:
    tab1,tab2 = st.tabs(['by Win/Loss','by Team'])
    with tab1:
        newnames={'True':'Win','False':'Loss'}

        scatter_fig = px.scatter(temp_df,
                                x='week',
                                y='total_pts',
                                color='win_loss',
                                template='plotly_dark',
                                size='total_pts',
                                size_max=9,
                                hover_name=ticktext*8,
                                color_discrete_sequence=px.colors.qualitative.Pastel1,
                                labels={'week':'','total_pts':'Points Scored'},
                                custom_data=['team','cuts_made','players_started','win_loss','median_delta','total_pts','opponent'],
                                height=400,
                                render_mode='svg'
                                ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,
                                                legend=dict(orientation='h',yanchor="bottom",y=1.1,x=.33,title='',font_color='#5A5856')
                                ).update_xaxes(tickvals = tickvals,ticktext = ticktext,
                                               tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14)
                                ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),
                                               tickcolor='darkgrey', gridcolor='darkgrey'
                                ).update_traces(marker=dict(size=10,opacity=.8,line=dict(width=.5,color='darkslategrey'))
                                ).for_each_trace(lambda t: t.update(name = newnames[t.name],
                                                                    legendgroup = newnames[t.name],
                                                                    hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                                                    ))
    
        scatter_fig.update_traces(hovertemplate=
                            "<b>%{customdata[0]}</b> \
                            <br>vs. %{customdata[6]}</b> \
                            <br> \
                            <br>Scored %{customdata[5]} Points</b> \
                            <br>%{customdata[4]} vs Median Score</b> \
                            <br> \
                            <br>%{customdata[1]}/%{customdata[2]} thru cut</b>")

        st.markdown("##")
        st.markdown("##")
        st.markdown("<center><h5>LEAGUE SCORING</h5></center>",unsafe_allow_html=True)
        st.plotly_chart(scatter_fig,use_container_width=True, config=config)

    with tab2:
        scatter_fig = px.scatter(temp_df,
                                x='week',
                                y='total_pts',
                                color='team',
                                template='plotly_dark',
                                hover_name=ticktext*8,
                                color_discrete_map=team_color,
                                labels={'week':'','total_pts':'Points Scored'},
                                custom_data=['team','cuts_made','players_started','win_loss','median_delta','total_pts','opponent'],
                                height=400
                                ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,
                                                legend=dict(orientation='h',yanchor="bottom",y=1.1,xanchor="center",x=.5,title='',font_color='#5A5856')
                                ).update_xaxes(tickvals = tickvals,ticktext = ticktext,
                                               tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14)
                                ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),
                                               tickcolor='darkgrey', gridcolor='darkgrey'
                                ).update_traces(marker=dict(size=10,opacity=.75,line=dict(width=.5,color='darkslategrey'))
                                )


        scatter_fig.update_traces(hovertemplate=
                            "<b>%{customdata[0]}</b> \
                            <br>vs. %{customdata[6]}</b> \
                            <br> \
                            <br>Scored %{customdata[5]} Points</b> \
                            <br>%{customdata[4]} vs Median Score</b> \
                            <br> \
                            <br>%{customdata[1]}/%{customdata[2]} thru cut</b>")

        st.markdown("##")
        st.markdown("##")
        st.markdown("<center><h5>LEAGUE SCORING</h5></center>",unsafe_allow_html=True)
        st.plotly_chart(scatter_fig,use_container_width=True, config=config)

### FINISHING POSITION COMPARISON
finish_place_container = st.container(border=True)
with finish_place_container:
    tab1,tab2 = st.tabs(['Log Scale', 'Regular Scale'])
    with tab1:
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
                height=550,
                ).update_traces(marker=dict(size=11,opacity=.75,line=dict(width=.5,color='darkslategrey'))
                ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(font_color='#5A5856',title="",orientation='h',y=1.15)
                ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14)
                ).update_xaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14))

        st.markdown("##")
        st.markdown("##")
        st.markdown("<center><h5>Median Finishing Place</h5></center>",unsafe_allow_html=True)
        st.plotly_chart(fin_place_scatter,use_container_width=True, config=config)
    with tab2:
        finish_medians = round(df[['team','fin_1','fin_2','fin_3','fin_4','fin_5','fin_6']].groupby('team').median(),1).reset_index()
        finish_medians.columns = 'Team','Best Finisher','2nd','3rd','4th','5th','Worst Finisher'
        melted_finish_medians = finish_medians.melt(id_vars='Team',value_vars=['Best Finisher','2nd','3rd','4th','5th','Worst Finisher'])

        fin_place_scatter = px.scatter(melted_finish_medians,
                x='variable',
                y='value',
                color='Team',
                color_discrete_map=team_color,
                template='plotly_white',
                labels={'value':'Finish Place<br>','variable':''},
                height=550,
                ).update_traces(marker=dict(size=11,opacity=.75,line=dict(width=.5,color='darkslategrey'))
                ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(font_color='#5A5856',title="",orientation='h',y=1.15)
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
        st.markdown(f"<center><h5>Correlation<br>to WINS</h5></center>",unsafe_allow_html=True)
        "#"
        st.markdown(f"Choose a Statistic<br>",unsafe_allow_html=True)
        radio_options = [
            {"label": "Birdie : Bogey Ratio", "value": "bb_ratio", "id": "bb_ratio"},
            {"label": "Points / hole", "value": "pp_hole", "id": "pp_hole"},
            {"label": "Cuts Made / wk", "value": "cuts_made", "id": "cuts_made"},
            {"label": "Place Pts / wk", "value": "plc_pts", "id": "plc_pts"},
            {"label": "Pars / wk", "value": "pars_num", "id": "pars_num"},
            {"label": "Birdies / wk", "value": "bird_num", "id": "bird_num"},
            {"label": "Eagles / wk", "value": "eag_num", "id": "eag_num"},
            {"label": "Bogeys / wk", "value": "bog_num", "id": "bog_num"},
            {"label": "Pts vs. Weekly Median", "value": "median_delta", "id": "median_delta"}
        ]
        radio_value = ui.radio_group(options=radio_options, default_value="bb_ratio", key="radio1")

    with col2:
        "#"
        r_squared = st.empty()
        df['bb_ratio'] = round(df.bird_num / df.bog_num,1)
        # df['avg_place_pts'] = round(df.plc_pts / df.TP)
        fig = px.scatter(df.groupby(['team'],as_index=False)[[radio_value,'win_loss']].agg({radio_value:'mean','win_loss':'sum'}),
                    x=radio_value,
                    y='win_loss',
                    color='team',
                    color_discrete_map=team_color,
                    trendline='ols',trendline_scope='overall',trendline_color_override='black',
                    labels={'win_loss':'Wins',radio_value:stats_dict[radio_value]}
                ).update_traces(marker=dict(size=20,opacity=.75,line=dict(width=1,color='darkslategrey'))
                ).update_layout(showlegend=False#legend=dict(title=None,orientation='h',x=0,y=1.3))
                ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14), tickvals=tickvals
                ).update_xaxes(showgrid=True,gridcolor="#B1A999",tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14))

        results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
        r_squared.markdown(f"<h5><center>R-Squared: {results:.2f}</center></h5>", unsafe_allow_html=True)

        st.plotly_chart(fig,use_container_width=True, config=config)