import streamlit as st

from app import db, queries

TTL = 600  # secondi: i dati cambiano solo quando si rilancia l'ETL


@st.cache_data(ttl=TTL)
def seasons():
    return queries.list_seasons(db.get_engine())


@st.cache_data(ttl=TTL)
def teams(season):
    return queries.list_teams(db.get_engine(), season)


@st.cache_data(ttl=TTL)
def standings(season):
    return queries.standings(db.get_engine(), season)


@st.cache_data(ttl=TTL)
def recent_form(season, team, n=5):
    return queries.recent_form(db.get_engine(), season, team, n)


@st.cache_data(ttl=TTL)
def team_summary(season, team):
    return queries.team_summary(db.get_engine(), season, team)


@st.cache_data(ttl=TTL)
def home_away_points(season, team):
    return queries.home_away_points(db.get_engine(), season, team)


@st.cache_data(ttl=TTL)
def trends():
    return queries.season_trends(db.get_engine())


@st.cache_data(ttl=TTL)
def discipline(season):
    return queries.discipline_by_team(db.get_engine(), season)
