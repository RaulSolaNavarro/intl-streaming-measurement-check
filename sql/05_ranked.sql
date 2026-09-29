-- 05_ranked
-- The comparison set: every charting title-market-week that has a Wikipedia
-- article in the market's language and usable pageviews that week (status
-- `kept` in 04_title_week_status), with both sources ranked inside it.
-- Weeks before an article's first recorded view, and the partial week in
-- which that first view falls, are treated as missing and left out before
-- ranking, so n counts only titles with a full week of attention data.
--
-- Ranks are computed within each variant, market, week, and category (Films
-- and TV separately, as Netflix publishes them). Both ranks run 1..n inside
-- that set, so they are on the same scale:
--   netflix_rank_in_set   from Netflix's published rank (1 = most viewed)
--   pageview_rank_in_set  from weekly pageviews (1 = most views)
-- Ties get the average of the tied positions (the standard Spearman
-- convention): RANK() gives the lowest tied position, and adding
-- (tie count - 1) / 2 moves it to the middle of the tied block.
--
-- Two variants are stacked so every later step can report both:
--   all                   every kept pair
--   excl_contested_kept   drops pairs whose Netflix-ID match was contested
--                         and kept (see data/logs/contested_pairs.csv)
--
-- rank_norm columns rescale ranks to 0..1 as (rank - 1) / (n - 1), so weeks
-- with different n can be pooled. They are NULL when n = 1.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.ranked` AS
WITH base AS (
  SELECT
    w.title_id, w.show_title, w.category, w.market, w.week_start, w.week_end,
    w.netflix_rank, w.cumulative_weeks,
    m.lang, m.article, m.qid, m.match_method, m.match_status,
    p.views
  FROM `intl-streaming-measurement.streaming_measurement.title_market_week` AS w
  JOIN `intl-streaming-measurement.streaming_measurement.title_article_map` AS m
    USING (title_id, market)
  JOIN `intl-streaming-measurement.streaming_measurement.pageviews_weekly` AS p
    USING (title_id, market, week_end)
  JOIN `intl-streaming-measurement.streaming_measurement.title_week_status` AS s
    USING (title_id, market, week_end)
  WHERE s.status = 'kept'
),
variants AS (
  SELECT 'all' AS variant, * FROM base
  UNION ALL
  SELECT 'excl_contested_kept' AS variant, * FROM base
  WHERE match_status != 'contested_kept'
),
ranked AS (
  SELECT
    *,
    COUNT(*) OVER grp AS n,
    -- Netflix ranks are unique within a category-week, so no tie adjustment.
    RANK() OVER (PARTITION BY variant, market, week_end, category ORDER BY netflix_rank)
      AS netflix_rank_in_set,
    RANK() OVER (PARTITION BY variant, market, week_end, category ORDER BY views DESC)
      + (COUNT(*) OVER (PARTITION BY variant, market, week_end, category, views) - 1) / 2
      AS pageview_rank_in_set
  FROM variants
  WINDOW grp AS (PARTITION BY variant, market, week_end, category)
)
SELECT
  *,
  SAFE_DIVIDE(netflix_rank_in_set - 1, n - 1)  AS netflix_rank_norm,
  SAFE_DIVIDE(pageview_rank_in_set - 1, n - 1) AS pageview_rank_norm
FROM ranked;
