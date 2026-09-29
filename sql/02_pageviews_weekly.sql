-- 02_pageviews_weekly
-- Daily Wikipedia pageviews summed into Netflix weeks (Monday to Sunday).
--
-- DATE_TRUNC(..., WEEK(MONDAY)) gives the Monday that starts each day's week;
-- adding 6 days gives the Sunday, which matches Netflix's week_end. The
-- lead-in weeks before the Netflix window are kept (the timing step uses
-- them). `days` should be 7 for every complete week.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.pageviews_weekly` AS
SELECT
  title_id,
  market,
  lang,
  article,
  DATE_ADD(DATE_TRUNC(date, WEEK(MONDAY)), INTERVAL 6 DAY) AS week_end,
  SUM(views)                                                AS views,
  COUNT(*)                                                  AS days
FROM `intl-streaming-measurement.streaming_measurement.pageviews_daily`
GROUP BY title_id, market, lang, article, week_end;
