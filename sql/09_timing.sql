-- 09_timing
-- Days between a title's pageview peak and the start of its first Netflix
-- chart week, per title-market pair.
--
--   days_peak_vs_chart = peak_date - first chart week's Monday
--   negative -> attention peaked before the title first charted
--   0..6     -> peak during the first chart week
--   positive -> attention peaked after it first charted
--
-- Censoring flags (rows are kept; later steps filter on them):
--   left_censored      the title was already in the Top 10 before the window
--                      opened (first week in the window is the window's first
--                      week and Netflix's cumulative count is above 1), so its
--                      true first chart week is unknown.
--   peak_at_range_edge the peak falls on the first or last day of the
--                      pageview range, so the true peak may lie outside it.
--   no_views           the article had no pageviews at all in the range.
--   article_after_chart the article's first recorded view came after the
--                      title first charted (03_article_coverage). The peak
--                      then reflects when the article appeared as much as
--                      when attention rose, so these pairs are excluded from
--                      timing summaries.
-- Ties for the peak day go to the earliest date.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.timing` AS
WITH bounds AS (
  SELECT MIN(date) AS range_start, MAX(date) AS range_end,
         (SELECT MIN(week_end) FROM `intl-streaming-measurement.streaming_measurement.title_market_week`)
           AS window_first_week
  FROM `intl-streaming-measurement.streaming_measurement.pageviews_daily`
),
first_chart AS (
  -- First chart week per pair, and Netflix's cumulative count in that week.
  SELECT title_id, market, category, show_title,
         ARRAY_AGG(STRUCT(week_start, week_end, cumulative_weeks)
                   ORDER BY week_end LIMIT 1)[OFFSET(0)] AS fw
  FROM `intl-streaming-measurement.streaming_measurement.title_market_week`
  GROUP BY title_id, market, category, show_title
),
peak AS (
  SELECT title_id, market,
         ARRAY_AGG(STRUCT(date, views) ORDER BY views DESC, date LIMIT 1)[OFFSET(0)] AS pk,
         SUM(views) AS total_views
  FROM `intl-streaming-measurement.streaming_measurement.pageviews_daily`
  GROUP BY title_id, market
)
SELECT
  f.title_id, f.show_title, f.category, f.market,
  m.lang, m.article, m.match_status,
  f.fw.week_start                                   AS first_week_start,
  f.fw.week_end                                     AS first_week_end,
  f.fw.cumulative_weeks                             AS cumulative_weeks_at_first,
  p.pk.date                                         AS peak_date,
  p.pk.views                                        AS peak_views,
  p.total_views,
  DATE_DIFF(p.pk.date, f.fw.week_start, DAY)        AS days_peak_vs_chart,
  (f.fw.week_end = b.window_first_week AND f.fw.cumulative_weeks > 1) AS left_censored,
  p.pk.date IN (b.range_start, b.range_end)         AS peak_at_range_edge,
  p.total_views = 0                                 AS no_views,
  IFNULL(c.first_view_date > f.fw.week_start, FALSE) AS article_after_chart
FROM first_chart AS f
JOIN `intl-streaming-measurement.streaming_measurement.title_article_map` AS m
  USING (title_id, market)
JOIN peak AS p USING (title_id, market)
JOIN `intl-streaming-measurement.streaming_measurement.article_coverage` AS c
  USING (title_id, market)
CROSS JOIN bounds AS b;
