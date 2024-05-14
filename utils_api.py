import os
import json
import requests

import streamlit as st


# _dir_pkg_root = os.path.dirname(__file__)

dg_key = st.secrets.dg_key


def load_secrets():
    fn_secrets = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fantrax.secrets",
    )
    with open(fn_secrets, "r") as fsecrets:
        secrets = json.load(fsecrets)
    return secrets


def dump_to_json(fn_json, data):
    with open(fn_json, "w") as f_json:
        json.dump(data, f_json, indent=4)


def rest_request(url,body,note="",resp_format="json",):
    if resp_format == "json":
        headers = {"Content-Type": "application/json"}
    elif resp_format == "csv":
        headers = {"Content-Type": "application/csv"}

    response = requests.post(url,
                             data=json.dumps(body),
                             headers=headers,)
    print(f"{note}status code:", response.status_code)

    if resp_format == "json":
        return response.json()
    elif resp_format == "csv":
        return response.text
    else:
        return response

def fetch_leagueInfo(leagueId=None,secrets=load_secrets()):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_leagueInfo = (f"https://www.fantrax.com/fxea/general/getLeagueInfo?leagueId={leagueId}")
    body_leagueInfo = {}

    leagueInfo = rest_request(url_leagueInfo,
                              body_leagueInfo,
                              note="requesting league info. ")
    return leagueInfo

def fetch_teamRosters(
    leagueId=None,
    secrets=load_secrets(),
):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_teamRosters = (
        f"https://www.fantrax.com/fxea/general/getTeamRosters?leagueId={leagueId}"
    )
    body_teamRosters = {
        # "leagueId":secrets["league_id"],
    }
    teamRosters = rest_request(
        url_teamRosters,
        body_teamRosters,
        note="requesting team rosters. ",
    )
    return teamRosters

def fetch_leagueStandings(
    leagueId=None,
    secrets=load_secrets(),
):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_leagueStandings = (
        f"https://www.fantrax.com/fxea/general/getStandings?leagueId={leagueId}"
    )
    body_leagueStandings = {
        # "leagueId":secrets["league_id"],
    }
    leagueStandings = rest_request(
        url_leagueStandings,
        body_leagueStandings,
        note="requesting league standings. ",
    )
    return leagueStandings

def fetch_draftResults(
    leagueId=None,
    secrets=load_secrets(),
):
    if leagueId is None:
        leagueId = secrets["league_id"]

    url_draftResults = (
        f"https://www.fantrax.com/fxea/general/getDraftResults?leagueId={leagueId}"
    )
    body_draftResults = {
        # "leagueId":secrets["league_id"],
    }
    draftResults = rest_request(
        url_draftResults,
        body_draftResults,
        note="requesting draft results. ",
    )
    return draftResults