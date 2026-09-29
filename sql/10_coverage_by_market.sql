-- 10_coverage_by_market
-- Coverage metric: how quickly each language edition's article follows a
-- title onto the Netflix chart, by market and category.
--
-- Built on 03_article_coverage (one row per title-market pair with an
-- article). days_chart_to_first_view = first recorded view minus the Monday
-- of the first chart week. Articles already read before the pageview range
-- began are counted as "covered before charting"; their exact lead is
-- unknown, so they are left out of the day quantiles and counted separately.
--
-- Columns
--   pairs                    title-market pairs with an article
--   covered_before_range     article already had views on the range's first day
--   covered_by_chart_start   first view on or before the first chart Monday
--   appeared_after_chart     first view after the first chart Monday
--   no_views                 article never viewed in the range
--   days_q1 / median / q3    quartiles of days_chart_to_first_view, among
--                            pairs whose first view falls inside the range

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.coverage_by_market` AS
SELECT
  market,
  category,
  COUNT(*)                                                            AS pairs,
  COUNTIF(article_before_range)                                       AS covered_before_range,
  COUNTIF(days_chart_to_first_view <= 0)                              AS covered_by_chart_start,
  COUNTIF(days_chart_to_first_view > 0)                               AS appeared_after_chart,
  COUNTIF(first_view_date IS NULL)                                    AS no_views,
  APPROX_QUANTILES(IF(article_before_range, NULL, days_chart_to_first_view), 4 IGNORE NULLS)[SAFE_OFFSET(1)] AS days_q1,
  APPROX_QUANTILES(IF(article_before_range, NULL, days_chart_to_first_view), 4 IGNORE NULLS)[SAFE_OFFSET(2)] AS days_median,
  APPROX_QUANTILES(IF(article_before_range, NULL, days_chart_to_first_view), 4 IGNORE NULLS)[SAFE_OFFSET(3)] AS days_q3
FROM `intl-streaming-measurement.streaming_measurement.article_coverage`
GROUP BY market, category;
