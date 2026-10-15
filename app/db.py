import streamlit as st
from sqlalchemy import create_engine, text

from etl import config


def check_connection(engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@st.cache_resource
def get_engine():
    return create_engine(config.db_url(), pool_pre_ping=True)
