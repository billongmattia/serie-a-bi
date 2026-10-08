import re

from sqlalchemy import text

from etl import config

CHECKS_PATH = config.ROOT / "sql" / "03_quality_checks.sql"

# Punti ufficiali dei campioni d'Italia: (inizio stagione, squadra) -> punti
EXPECTED_POINTS = {(2016, "Juventus"): 91, (2023, "Inter"): 94}

POINTS_QUERY = text(
    "SELECT SUM(f.points) FROM fact_team_match f "
    "JOIN dim_match m ON m.match_key = f.match_key "
    "JOIN dim_team t ON t.team_key = f.team_key "
    "WHERE m.season_key = :season AND t.team_name = :team"
)


SEASON_MATCHES_QUERY = text("SELECT COUNT(*) FROM dim_match WHERE season_key = :season")


def parse_checks(sql_text: str) -> dict[str, str]:
    checks: dict[str, str] = {}
    name, buffer = None, []
    for line in sql_text.splitlines():
        match = re.match(r"--\s*check:\s*(.+)", line)
        if match:
            if name:
                checks[name] = "\n".join(buffer).strip().rstrip(";")
            name, buffer = match.group(1).strip(), []
        elif name:
            buffer.append(line)
    if name:
        checks[name] = "\n".join(buffer).strip().rstrip(";")
    return checks


def run_quality_checks(engine, sql_text: str | None = None) -> list[str]:
    checks = parse_checks(sql_text or CHECKS_PATH.read_text(encoding="utf-8"))
    problems: list[str] = []
    with engine.connect() as conn:
        for name, query in checks.items():
            rows = conn.execute(text(query)).fetchall()
            if rows:
                problems.append(f"{name}: {len(rows)} righe in violazione")
        for (season, team), expected in EXPECTED_POINTS.items():
            matches = conn.execute(SEASON_MATCHES_QUERY, {"season": season}).scalar()
            if not matches:
                continue  # stagione non caricata: niente da verificare
            actual = conn.execute(POINTS_QUERY, {"season": season, "team": team}).scalar()
            if actual is None:
                problems.append(f"punti {team} {season}: squadra non trovata (nome cambiato?)")
            elif int(actual) != expected:
                problems.append(f"punti {team} {season}: attesi {expected}, trovati {int(actual)}")
    return problems
