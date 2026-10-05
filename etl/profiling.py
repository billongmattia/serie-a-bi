from pathlib import Path

import pandas as pd

from etl.extract import season_label
from etl.rawio import read_raw_csv

COLUMNS = ["HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"]


def _classify(df: pd.DataFrame, column: str) -> str:
    if column not in df.columns or len(df) == 0:
        return "no"
    ratio = df[column].notna().mean()
    if ratio >= 0.95:
        return "sì"
    return "parziale" if ratio > 0 else "no"


def coverage_matrix(paths: dict[int, Path]) -> pd.DataFrame:
    rows = []
    for year, path in sorted(paths.items()):
        df = read_raw_csv(path)
        row = {"stagione": season_label(year), "partite": len(df)}
        for column in COLUMNS:
            row[column] = _classify(df, column)
        rows.append(row)
    return pd.DataFrame(rows)


def to_markdown(matrix: pd.DataFrame) -> str:
    headers = list(matrix.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for _, row in matrix.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines) + "\n"


def write_report(matrix: pd.DataFrame, out_path: Path) -> None:
    text = (
        "# Copertura delle colonne per stagione\n\n"
        "`sì` = presente in almeno il 95% delle partite; `parziale` = presente "
        "in alcune; `no` = assente. Dove non c'è copertura il dato resta NULL. "
        "La colonna `Referee` non è analizzata: nel dataset è sempre vuota.\n\n"
        + to_markdown(matrix)
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    from etl import config
    from etl.extract import extract_all

    paths, _ = extract_all()
    write_report(coverage_matrix(paths), config.ROOT / "docs" / "coverage.md")
    print("Scritto docs/coverage.md")
