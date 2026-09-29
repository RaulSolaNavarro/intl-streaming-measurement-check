-- 04_agreement_weekly
-- Spearman rank correlation per variant, market, category, and week.
--
-- Spearman's rho is the Pearson correlation of the ranks, so CORR() on the
-- within-set ranks gives it directly, with ties handled by the average ranks
-- from 03_ranked. rho = 1 means pageviews order the titles exactly as Netflix
-- does; 0 means no relationship; -1 means the reverse order.
--
-- Weekly rho is only computed where n >= 4. Smaller sets are kept in the
-- table with rho = NULL so the coverage of each market stays visible. The
-- report shows weekly rho as a distribution; the headline metric is the
-- pooled correlation in 05_agreement_pooled.
-- CORR() also returns NULL when one side has no variation (for example
-- every title had zero pageviews that week).

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.agreement_weekly` AS
SELECT
  variant,
  market,
  category,
  week_end,
  COUNT(*)                                                   AS n,
  COUNT(*) >= 4                                              AS meets_min_n,
  IF(COUNT(*) >= 4, CORR(netflix_rank_in_set, pageview_rank_in_set), NULL) AS spearman_rho
FROM `intl-streaming-measurement.streaming_measurement.ranked`
GROUP BY variant, market, category, week_end;
