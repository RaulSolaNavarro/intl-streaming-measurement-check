-- 03_article_coverage
-- When did each title-market pair's Wikipedia article start receiving
-- views, relative to the title's first Netflix chart week?
--
-- first_view_date is the first day with at least one pageview in the pulled
-- range. It stands in for "the article existed from this day". The creation
-- timestamp from the Wikipedia API is not used, because an article can be
-- created as a redirect and filled in much later, which makes creation
-- dates misleading. Pageviews to a redirect page are not counted under the
-- target article, so the first recorded view is the better signal.
--
--   days_chart_to_first_view = first_view_date - first chart week's Monday
--   negative or 0  -> article already had views when the title first charted
--   positive       -> the article appeared (or started being read) after
--                     the title was already charting
--
-- Articles already receiving views on the first day of the range get
-- first_view_date = range start and article_before_range = TRUE: their true
-- first view is earlier and unknown, which is fine, they were covered.
-- Pairs with no views at all have first_view_date NULL.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.article_coverage` AS
WITH first_view AS (
  SELECT title_id, market,
         MIN(IF(views > 0, date, NULL)) AS first_view_date,
         MIN(date)                      AS range_start
  FROM `intl-streaming-measurement.streaming_measurement.pageviews_daily`
  GROUP BY title_id, market
),
first_chart AS (
  SELECT title_id, market, category, show_title,
         MIN(week_start) AS first_week_start
  FROM `intl-streaming-measurement.streaming_measurement.title_market_week`
  GROUP BY title_id, market, category, show_title
)
SELECT
  c.title_id, c.show_title, c.category, c.market,
  m.lang, m.article, m.match_status,
  c.first_week_start,
  v.first_view_date,
  v.first_view_date = v.range_start                         AS article_before_range,
  DATE_DIFF(v.first_view_date, c.first_week_start, DAY)     AS days_chart_to_first_view
FROM first_chart AS c
JOIN `intl-streaming-measurement.streaming_measurement.title_article_map` AS m
  USING (title_id, market)
JOIN first_view AS v USING (title_id, market);
