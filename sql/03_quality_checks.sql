-- check: ogni stagione ha 380 partite
SELECT season_key, COUNT(*) AS partite
FROM dim_match
GROUP BY season_key
HAVING COUNT(*) <> 380;

-- check: ogni stagione ha 20 squadre
SELECT m.season_key, COUNT(DISTINCT f.team_key) AS squadre
FROM fact_team_match f
JOIN dim_match m ON m.match_key = f.match_key
GROUP BY m.season_key
HAVING COUNT(DISTINCT f.team_key) <> 20;

-- check: ogni partita ha esattamente due righe di fatto
SELECT m.match_key
FROM dim_match m
LEFT JOIN fact_team_match f ON f.match_key = m.match_key
GROUP BY m.match_key
HAVING COUNT(f.match_key) <> 2;

-- check: i punti di una partita sono 2 o 3
SELECT match_key, SUM(points) AS punti
FROM fact_team_match
GROUP BY match_key
HAVING SUM(points) NOT IN (2, 3);

-- check: gol fatti e subiti sono coerenti tra casa e trasferta
SELECT h.match_key
FROM fact_team_match h
JOIN fact_team_match a ON a.match_key = h.match_key AND a.is_home = 0
WHERE h.is_home = 1
  AND (h.goals_for <> a.goals_against OR h.goals_against <> a.goals_for);
