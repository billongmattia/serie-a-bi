CREATE TABLE IF NOT EXISTS dim_season (
    season_key INT PRIMARY KEY,
    label      VARCHAR(7) NOT NULL,
    start_year INT NOT NULL,
    end_year   INT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    `date`   DATE NOT NULL,
    `day`    INT NOT NULL,
    `month`  INT NOT NULL,
    `year`   INT NOT NULL,
    weekday  VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_team (
    team_key  INT PRIMARY KEY,
    team_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_match (
    match_key     INT PRIMARY KEY,
    match_id      CHAR(16) NOT NULL UNIQUE,
    date_key      INT NOT NULL,
    season_key    INT NOT NULL,
    matchday      INT NOT NULL,
    home_team_key INT NOT NULL,
    away_team_key INT NOT NULL,
    FOREIGN KEY (date_key)      REFERENCES dim_date (date_key),
    FOREIGN KEY (season_key)    REFERENCES dim_season (season_key),
    FOREIGN KEY (home_team_key) REFERENCES dim_team (team_key),
    FOREIGN KEY (away_team_key) REFERENCES dim_team (team_key)
);

CREATE TABLE IF NOT EXISTS fact_team_match (
    match_key         INT NOT NULL,
    team_key          INT NOT NULL,
    opponent_team_key INT NOT NULL,
    is_home           INT NOT NULL,
    goals_for         INT NOT NULL,
    goals_against     INT NOT NULL,
    goals_ht_for      INT,
    goals_ht_against  INT,
    shots_for         INT,
    shots_against     INT,
    shots_on_target_for     INT,
    shots_on_target_against INT,
    fouls_for         INT,
    fouls_against     INT,
    corners_for       INT,
    corners_against   INT,
    yellow_for        INT,
    red_for           INT,
    result            CHAR(1) NOT NULL,
    points            INT NOT NULL,
    PRIMARY KEY (match_key, team_key),
    FOREIGN KEY (match_key)         REFERENCES dim_match (match_key),
    FOREIGN KEY (team_key)          REFERENCES dim_team (team_key),
    FOREIGN KEY (opponent_team_key) REFERENCES dim_team (team_key)
);
