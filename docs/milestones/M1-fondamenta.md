# M1 – Fondamenta

**Stato:** ✅ completata · **Piano:** Task 1 · **Spiegazione:** [01-setup-e-database](../spiegazioni/01-setup-e-database.md)

**Obiettivo:** avere un ambiente di lavoro riproducibile: repository Git, Python isolato e un database MySQL con lo schema già pronto.

## Task
- [x] **M1.1** Inizializzare Git (`main`) e il `.gitignore`.
- [x] **M1.2** Creare il venv e installare le dipendenze (`requirements.txt`).
- [x] **M1.3** Scrivere `etl/config.py` (percorsi, stagioni, collegamento al database).
- [x] **M1.4** Scrivere lo schema SQL: staging (`sql/01_staging.sql`) e star schema (`sql/02_star_schema.sql`).
- [x] **M1.5** Avviare MySQL 8.4 con Docker Compose e verificare le 6 tabelle.

## Note
- MySQL è sulla porta **3308**: la 3306 è di un `mysqld` locale e la 3307 è del progetto Ludiq.

## Fatto quando
`docker compose up -d --wait` parte e `SHOW TABLES` mostra `stg_matches`, `dim_season`, `dim_date`, `dim_team`, `dim_match`, `fact_team_match`.
