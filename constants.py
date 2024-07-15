import streamlit as st

dg_key = st.secrets.dg_key

TOURNAMENT_NAME = "The Open"
WEEK_NUMBER = 27
CUTLINE = 66

LIVE_STATS = f"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key={dg_key}"
FANTASY_PROJECTIONS = f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}"

tickvals = [1,2,3,4,5,6,7,8,9,10, \
            11,12,13,14,15,16,17,18,19,20, \
            21,22,23,24,25,26]

ticktext = ['Sony','Amex','Farmers','AT&T','Waste Mgmt','Genesis','Mexico Open', \
            'Cognizant','Arnold Palmer','PLAYERS', \
            'Valspar','Houston Open','Valero','The Masters','RBC Heritage','AT&T Byron Nelson',\
            'Wells Fargo','PGA Championship','Charles Schwab', 'RBC Canadian', \
            'The Memorial','US Open','Travelers','Rocket Mortgage','John Deere Classic', 'Scottish Open']

no_cut_weeks = [4,15,17,21,23]