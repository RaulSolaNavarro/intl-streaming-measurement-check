-- 04_title_week_status
-- Every charting title-market-week that has an article, labelled with
-- whether its pageviews can be used.
--
--   kept               the article had views on or before the week's Monday
--   partial_week       the first recorded view falls inside the week, so the
--                      week's total covers only part of it
--   before_first_view  the week ends before the first recorded view; the
--                      article most likely didn't exist yet, so the zero is
--                      missing data, not zero attention
--   no_views           the article had no views anywhere in the range
--
-- Only `kept` rows go on to ranking (05_ranked). The other statuses are
-- counted in the Phase 2 summary.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.title_week_status` AS
SELECT
  w.title_id, w.show_title, w.category, w.market, w.week_start, w.week_end,
  c.first_view_date,
  CASE
    WHEN c.first_view_date IS NULL          THEN 'no_views'
    WHEN w.week_end < c.first_view_date     THEN 'before_first_view'
    WHEN w.week_start < c.first_view_date   THEN 'partial_week'
    ELSE 'kept'
  END AS status
FROM `intl-streaming-measurement.streaming_measurement.title_market_week` AS w
JOIN `intl-streaming-measurement.streaming_measurement.article_coverage` AS c
  USING (title_id, market);
