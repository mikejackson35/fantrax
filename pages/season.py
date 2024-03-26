import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
from utils import team_color
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
    season_data = pd.read_excel(r"fantrax_season_data.xlsm")
    return season_data
df = get_season_data()

# ###  PER TOURNAMENT AVERAGES  ###
st.write("")
st.markdown("<center><h5>WEEKLY AVERAGES</h5></center>",unsafe_allow_html=True)
team_stat_medians = df.groupby('team')[['total_pts','cuts_made','total_holes','pp_hole','bird_num','eag_num','bog_num','dbog_num','plc_pts']].mean()#.reset_index()
team_stat_medians.columns = 'Total Pts','Cuts Made','Holes Played','Pts/Hole','Birdies','Eagles','Bogeys','Doubles','Plc Pts'
team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']] = team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']].astype('int')
team_stat_medians = team_stat_medians.sort_values('Total Pts',ascending=False).round({'Cuts Made':1,'Pts/Hole':2,'Eagles':1,'Doubles':1})
st.dataframe(team_stat_medians,use_container_width=True)
##################

### SEASON TO DATE SCORE VS WEEKLY MEDIAN  ###
team_medians = pd.DataFrame(df.groupby('team',as_index=False)['median_delta'].sum()).sort_values(by='median_delta',ascending=False).reset_index(drop=True)
median_delta_bar = px.bar(team_medians,
                          text_auto='.2s',
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
median_delta_by_team_bar = px.bar(
    team_weekly_deltas.sort_values('median_delta',ascending=False),
    x='week',
    y='median_delta',
    color='team',
    color_discrete_map=team_color,        
    facet_col='team',
    facet_col_wrap=2,
    facet_col_spacing=.1,
    facet_row_spacing=.16,
    height=1000,
    width=800,
    labels={'median_delta':'','week':''},
    template='plotly_dark',
    text_auto='.3s'
    ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),tickcolor='darkgrey', gridcolor='darkgrey'
    ).update_xaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),showticklabels=True,tickmode='array',tickvals = [1,2,3,4,5,6,7,8,9,10,11],ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer','PLAYERS','Valspar'],ticklabelposition='outside'
    ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=False
    ).for_each_annotation(lambda a: a.update(text=a.text.replace("team=", "")))

st.markdown("##")
st.markdown("##")
st.markdown('<center><h5>vs. WEEKLY MEDIAN SCORE</h5></center>',unsafe_allow_html=True)
with st.expander("expand to see team-by-team weekly"):
    st.plotly_chart(median_delta_by_team_bar,config=config, use_container_width=True)
st.plotly_chart(median_delta_bar,config=config,use_container_width=True)
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
                        size='cuts_made',
                        size_max=12,
                        hover_name='win_loss',
                        color_discrete_sequence=px.colors.qualitative.Pastel1,
                        labels={'week':'','total_pts':'Points Scored'}
                        ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,
                                        legend=dict(orientation='h',yanchor="bottom",y=1,xanchor="center",x=.5,title='',font_color='#5A5856')
                        ).update_xaxes(tickangle= -45,tickvals = [1,2,3,4,5,6,7,8,9,10,11],
                                       ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer','PLAYERS','Valspar'],
                                       tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14)
                        ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),tickcolor='darkgrey', gridcolor='darkgrey'
                        ).update_traces(marker=dict(line_color='black')
                        ).for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

st.markdown("##")
st.markdown("##")
st.markdown("<center><h5>WEEKLY SCORES</h5></center>",unsafe_allow_html=True)
st.plotly_chart(scatter_fig,use_container_width=True, config=config)

### CUTS MADE DISTRIBUTION  ###
df['rounded_percentage'] = (df['cuts_made'] * 100).round().astype(int).astype(str) + '%'

cuts_made_hist1 = px.histogram(df.sort_values('cuts_made', ascending=False),
                              x='cuts_made',
                              template='plotly_dark',
                              labels={'cuts_made':'Players Thru Cut', 'count':''},
                              title="",
                              histnorm='percent',
                              color_discrete_sequence=['grey'],
                              height=300,
                              text_auto='.2s'
                             )

cuts_made_hist1.update_layout(bargap=0.2, legend=dict(title="", x=.45, y=1.2, orientation='h'))
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

st.markdown("##")
st.markdown("##")
st.markdown("<center><h5>Cuts Made Distribution (%)</h5></center>",unsafe_allow_html=True)
st.plotly_chart(cuts_made_hist1,use_container_width=True, config=config)

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
                    height=300
                             ).update_layout(legend=dict(title="",x=.45,y=1.2,orientation='h',font_color='#5A5856'))

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
st.markdown("<center><h5>Win % by Cuts Made</h5></center>",unsafe_allow_html=True)
st.plotly_chart(cuts_made_hist,use_container_width=True, config=config)

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


### CORRELATION TO WINS BY STAT

stats_dict = {
    'bb_ratio':'Birdie Bogey Ratio',
    'bird_num':'Num of Birdies',
    'median_delta':'+/- Weekly Median',
    'total_pts':'Fantasy Points',
    'plc_pts':'Place Points',
    'cuts_made':'Avg Cuts Made/Wk',
    'pp_hole':'Points per Hole Played',
    'pars_num':'Num of Pars',
    'eag_num':'Num of Eagles',
    'dbog_num':'Num of Double Bogeys',
    'bog_num':'Num of Bogeys'
}

st.write("##")
st.write("##")
st.markdown(f"<h5>Choose a statistic to observe it's correlation with 'Wins'</h5>",unsafe_allow_html=True)

stat = st.radio(
    "",
    ['bb_ratio','bird_num','median_delta','total_pts','plc_pts','cuts_made','pp_hole','pars_num','eag_num','dbog_num','bog_num'],
    format_func=lambda x: stats_dict.get(x),
    horizontal=True
    )

df['bb_ratio'] = df.bird_num / df.bog_num
scatter_df = df.groupby(['team'],as_index=False)[[stat,'win_loss']].mean()
fig = px.scatter(scatter_df,
            x=stat,
            y='win_loss',
            color='team',
            color_discrete_map=team_color,
            trendline='ols',trendline_scope='overall',trendline_color_override='black',
            labels={'win_loss':'Win Rate',stat:stats_dict[stat]}
        ).update_traces(marker=dict(size=15,opacity=.75,line=dict(width=1,color='darkslategrey'))
        ).update_layout(showlegend=False#legend=dict(title=None,orientation='h',x=0,y=1.3))
        ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14)
        ).update_xaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14))

results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
st.markdown("##")
st.markdown(f"<h5>r-squared: {results:.2f}</h5>",unsafe_allow_html=True)
st.plotly_chart(fig,use_container_width=True, config=config)