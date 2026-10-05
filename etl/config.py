import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
TEAM_MAP_PATH = Path(__file__).resolve().parent / "team_names.csv"

FIRST_SEASON = 2016
LAST_SEASON = 2025
SEASONS = list(range(FIRST_SEASON, LAST_SEASON + 1))

URL_TEMPLATE = "https://datahub.io/football/italian-serie-a/_r/-/season-{code}.csv"


def db_url() -> str:
    user = os.environ.get("MYSQL_USER", "serie_a")
    password = os.environ.get("MYSQL_PASSWORD", "serie_a_pw")
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3308")
    database = os.environ.get("MYSQL_DATABASE", "serie_a")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
