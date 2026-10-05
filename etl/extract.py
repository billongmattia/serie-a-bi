import logging
from pathlib import Path

import requests

from etl import config

log = logging.getLogger(__name__)


def season_code(start_year: int) -> str:
    return f"{start_year % 100:02d}{(start_year + 1) % 100:02d}"


def season_label(start_year: int) -> str:
    return f"{start_year}/{(start_year + 1) % 100:02d}"


def default_fetch(url: str) -> bytes:
    response = requests.get(
        url, timeout=30, headers={"User-Agent": "serie-a-bi-portfolio/1.0"}
    )
    response.raise_for_status()
    return response.content


def looks_like_csv(content: bytes) -> bool:
    return content.lstrip(b"\xef\xbb\xbf").startswith(b"Date,")


def extract_season(start_year, raw_dir=config.RAW_DIR, fetch=default_fetch) -> Path:
    path = Path(raw_dir) / f"season-{season_code(start_year)}.csv"
    if path.exists():
        return path
    url = config.URL_TEMPLATE.format(code=season_code(start_year))
    content = fetch(url)
    if not looks_like_csv(content):
        raise ValueError(f"{url} non ha restituito un CSV (inizio: {content[:40]!r})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def extract_all(seasons=config.SEASONS, raw_dir=config.RAW_DIR, fetch=default_fetch):
    paths: dict[int, Path] = {}
    failures: dict[int, str] = {}
    for year in seasons:
        try:
            paths[year] = extract_season(year, raw_dir, fetch)
        except Exception as exc:  # una stagione fallita non blocca le altre
            failures[year] = str(exc)
            log.error("Stagione %s non scaricata: %s", season_label(year), exc)
    return paths, failures


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    got, failed = extract_all()
    print(f"Scaricate/in cache: {sorted(got)}")
    print(f"Fallite: {failed}")
