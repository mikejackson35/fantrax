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
st.markdown("<center><h5>WEEKLY MEDIANS</h5></center>",unsafe_allow_html=True)
team_stat_medians = df.groupby('team')[['total_pts','cuts_made','total_holes','pp_hole','bird_num','eag_num','bog_num','dbog_num','plc_pts']].mean()#.reset_index()
team_stat_medians.columns = 'Total Pts','Cuts Made','Holes Played','Pts/Hole','Birdies','Eagles','Bogeys','Doubles','Plc Pts'
team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']] = team_stat_medians[['Total Pts','Holes Played','Bogeys','Birdies','Plc Pts']].astype('int')
team_stat_medians = team_stat_medians.sort_values('Total Pts',ascending=False).round({'Cuts Made':1,'Pts/Hole':2,'Eagles':1,'Doubles':1})
st.dataframe(team_stat_medians,use_container_width=True)
st.markdown('#')
##################

### SEASON TO DATE SCORE VS WEEKLY MEDIAN  ###
team_medians = pd.DataFrame(df.groupby('team',as_index=False)['median_delta'].sum()).sort_values(by='median_delta',ascending=False).reset_index(drop=True)
median_delta_bar = px.bar(team_medians,
                          text_auto='.2s',
                          color='team',
                          color_discrete_map=team_color,
                          template='plotly_dark',
                          labels={'index':'', 'value':''},
                          height=300
                         ).update_xaxes(showticklabels=False,tickfont=dict(color='#5A5856')
                         ).update_yaxes(showticklabels=False,showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856'
                         ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(y=1.75, orientation='h',title='',font_color='#5A5856'))

st.markdown("<center><h5>vs. WEEKLY MEDIAN</h5></center>",unsafe_allow_html=True)
st.plotly_chart(median_delta_bar,use_container_width=True)
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
                        title='Weekly Scores',
                        labels={'week':'','total_pts':'Points Scored'}
                        ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,title_x=.45,
                                        legend=dict(orientation='h',yanchor="bottom",y=1,xanchor="center",x=.5,title='',font_color='#5A5856')
                        ).update_xaxes(tickangle= -45,tickvals = [1,2,3,4,5,6,7,8,9,10,11],
                                       ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open','Cognizant','Arnold Palmer','PLAYERS','Valspar'],
                                       tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14)
                        ).update_yaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=14),tickcolor='darkgrey', gridcolor='darkgrey'
                        ).update_traces(marker=dict(line_color='black')
                        ).for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))


st.plotly_chart(scatter_fig)#,use_container_width=True, config=config)

### CUTS MADE DISTRIBUTION  ###
cuts_made_hist = px.histogram(df,
                    x='cuts_made',
                    text_auto='.2f',
                    template='plotly_dark',
                    labels={'cuts_made':'','count':''},
                    color='win_loss',
                    # histfunc='sum',
                    # histnorm='probability density',
                             ).update_layout(legend=dict(title=""))

cuts_made_hist.update_xaxes(tickvals = [2,3,4,5,6],
                            ticktext = ['2/6','3/6','4/6','5/6','6/6'])

cuts_made_hist.update_yaxes(showticklabels=False, showgrid=False,tickfont=dict(color='#5A5856'),title_font_color='#5A5856',visible= False)
st.markdown("<center><h5>Cuts Made Distribution</h5></center>",unsafe_allow_html=True)
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
          ).update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(font_color='#5A5856')
          ).update_yaxes(gridcolor="#B1A999", tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14)
          ).update_xaxes(showgrid=False,tickfont=dict(color='#5A5856'),title_font=dict(color='#5A5856',size=14))

st.plotly_chart(fin_place_scatter,use_container_width=True, config=config)


### CORRELATION TO WINS BY STAT - SCATTER PLOTS WITH SLIDER / TOGGLE / RADIO BUTTON FOR EACH STAT
df['bb_ratio'] = df.bird_num / df.bog_num
# stats_to_compare = ['pars_num','bird_num','eag_num','bog_num','dbog_num','plc_pts','cuts_made','median_delta','pp_hole','bb_ratio']
# df['bb_ratio'] = df.bird_num / df.bog_num

# for stat in stats_to_compare:
#     scatter_df = df.groupby(['team'],as_index=False)[[stat,'win_loss']].mean()
#     fig = px.scatter(scatter_df,
#               x=stat,
#               y='win_loss',
#               color='team',
#               color_discrete_map=team_color,
#               trendline='ols',trendline_scope='overall',trendline_color_override='black',
#           ).update_traces(marker_size=12
#           ).update_layout(legend=dict(title=None,orientation='h',x=0,y=1.3))
#     results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared

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

col1,col2 = st.columns([1,1.75])
with col1:
    st.write("##")
    st.write("##")
    st.write("##")
    stat = st.radio(
        "",
        ['bb_ratio','bird_num','median_delta','total_pts','plc_pts','cuts_made','pp_hole','pars_num','eag_num','dbog_num','bog_num'],
        format_func=lambda x: stats_dict.get(x),
    )

with col2:
    scatter_df = df.groupby(['team'],as_index=False)[[stat,'win_loss']].mean()
    fig = px.scatter(scatter_df,
                x=stat,
                y='win_loss',
                color='team',
                color_discrete_map=team_color,
                trendline='ols',trendline_scope='overall',trendline_color_override='black',
                title=f"Corr between {stat} vs Wins",
            ).update_traces(marker_size=12
            ).update_layout(showlegend=False)#legend=dict(title=None,orientation='h',x=0,y=1.3))
    results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
    st.markdown(f"<h3>R-Squared: {results:.2f}</h3>",unsafe_allow_html=True)
    st.plotly_chart(fig,use_container_width=True, config=config)



### CORRELATION TO WINS BY STAT - SCATTER PLOTS WITH SLIDER / TOGGLE / RADIO BUTTON FOR EACH STAT

# df['bb_ratio'] = df.bird_num / df.bog_num
# stats_to_compare = ['bb_ratio','bird_num','median_delta','total_pts','plc_pts','cuts_made','pp_hole','pars_num','eag_num','dbog_num','bog_num',]

# for stat in stats_to_compare:
#     scatter_df = df.groupby(['team'],as_index=False)[[stat,'win_loss']].sum()
#     fig = px.scatter(scatter_df,
#               x=stat,
#               y='win_loss',
#               color='team',
#               color_discrete_map=team_color,
#               template='plotly_white',
#               height=400,
#               width=600,
#               trendline='ols',trendline_scope='overall',trendline_color_override='black',
#               ).update_traces(marker=dict(size=15,line_color='black')
#               ).update_layout(showlegend=False)
#     results = px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
    # print(stat)
    # print(f"R-Squared Value: {results:.2f}")
    # print(fig.show())

# st.markdown(f"Comparing {stat} with Wins<br>R-Squared: {results:.2f}",unsafe_allow_html=True)
# st.plotly_chart(fig,use_container_width=True,config=config)