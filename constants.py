import streamlit as st

dg_key = st.secrets.dg_key

TOURNAMENT_NAME = "Rocket Mortgage"
WEEK_NUMBER = 24
CUTLINE = 66

LIVE_STATS = f"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key={dg_key}"
FANTASY_PROJECTIONS = f"https://feeds.datagolf.com/preds/fantasy-projection-defaults?tour=pga&site=draftkings&slate=main&file_format=csv&key={dg_key}"