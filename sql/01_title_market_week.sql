-- 01_title_market_week
-- One row per title, market, and Netflix week in which the title charted.
--
-- Netflix can list two seasons of the same show in one market-week. Seasons
-- roll up to the show (Wikipedia has one article per show), so the better
-- (lower) rank is kept. Netflix weeks run Monday to Sunday; `week` in the
-- source is the Sunday, stored here as week_end.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.title_market_week` AS
SELECT
  t.title_id,
  n.show_title,
  n.category,
  n.country_iso2                         AS market,
  n.week                                 AS week_end,
  DATE_SUB(n.week, INTERVAL 6 DAY)       AS week_start,
  MIN(n.weekly_rank)                     AS netflix_rank,        -- Netflix's published rank, 1-10
  MAX(n.cumulative_weeks_in_top_10)      AS cumulative_weeks     -- weeks in the Top 10 so far
FROM `intl-streaming-measurement.streaming_measurement.netflix_top10` AS n
JOIN `intl-streaming-measurement.streaming_measurement.titles` AS t
  USING (show_title, category)
GROUP BY t.title_id, n.show_title, n.category, n.country_iso2, n.week;
