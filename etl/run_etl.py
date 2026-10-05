import logging
import sys

from sqlalchemy import create_engine

from etl import config
from etl.extract import extract_all, season_label
from etl.load import build_staging, load_staging, load_star
from etl.quality import run_quality_checks
from etl.rawio import read_raw_csv
from etl.transform import load_team_map, transform_all

log = logging.getLogger("etl")


def setup_logging() -> None:
    log_dir = config.ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "etl.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> int:
    setup_logging()
    paths, failures = extract_all()
    if not paths:
        log.error("Nessun CSV disponibile: ETL interrotto")
        return 1

    raw_frames = {year: read_raw_csv(path) for year, path in paths.items()}
    star, rejected = transform_all(raw_frames, load_team_map(config.TEAM_MAP_PATH))

    engine = create_engine(config.db_url())
    load_staging(engine, build_staging(raw_frames))
    load_star(engine, star)
    problems = run_quality_checks(engine)

    log.info("Stagioni caricate: %s", [season_label(y) for y in sorted(paths)])
    log.info("Righe scartate per stagione: %s", rejected)
    log.info("Righe caricate: %s", {name: len(df) for name, df in star.items()})
    for year, message in failures.items():
        log.error("Stagione %s fallita: %s", season_label(year), message)
    for problem in problems:
        log.error("Controllo di qualità fallito: %s", problem)

    ok = not failures and not problems
    log.info("ETL terminato: %s", "OK" if ok else "CON PROBLEMI")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
