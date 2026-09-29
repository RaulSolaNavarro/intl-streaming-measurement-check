-- 05_agreement_pooled  (headline agreement metric)
-- Pooled within-market Spearman per variant, market, and category.
--
-- Titles are ranked within each week (03_ranked), then all title-weeks for
-- the market-category are pooled and correlated. The ranks are first
-- rescaled to 0..1 within each week ((rank - 1) / (n - 1)). Without that
-- step, pooling raw ranks inflates the correlation: a week with n = 8
-- contributes ranks up to 8 on both axes and a week with n = 2 only up to 2,
-- so the two axes move together just because n varies.
--
-- Weeks with n = 1 carry no ranking information and are left out. Weeks with
-- n = 2 or 3 are included; that is why this is the fallback for weeks too
-- small for a weekly rho.
--
-- Also reported: the weekly rho distribution for the same market-category
-- (weeks with n >= 4 only), so the headline and the week-to-week spread sit
-- side by side.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.agreement_pooled` AS
WITH pooled AS (
  SELECT
    variant,
    market,
    category,
    CORR(netflix_rank_norm, pageview_rank_norm)  AS pooled_rho,
    COUNT(*)                                     AS n_title_weeks,
    COUNT(DISTINCT week_end)                     AS n_weeks,
    COUNT(DISTINCT title_id)                     AS n_titles
  FROM `intl-streaming-measurement.streaming_measurement.ranked`
  WHERE n >= 2
  GROUP BY variant, market, category
),
weekly AS (
  SELECT
    variant,
    market,
    category,
    COUNTIF(spearman_rho IS NOT NULL)                          AS weeks_with_rho,
    APPROX_QUANTILES(spearman_rho, 4 IGNORE NULLS)             AS rho_quartiles  -- min, Q1, median, Q3, max
  FROM `intl-streaming-measurement.streaming_measurement.agreement_weekly`
  GROUP BY variant, market, category
)
SELECT
  p.*,
  w.weeks_with_rho,
  w.rho_quartiles[SAFE_OFFSET(0)] AS weekly_rho_min,
  w.rho_quartiles[SAFE_OFFSET(1)] AS weekly_rho_q1,
  w.rho_quartiles[SAFE_OFFSET(2)] AS weekly_rho_median,
  w.rho_quartiles[SAFE_OFFSET(3)] AS weekly_rho_q3,
  w.rho_quartiles[SAFE_OFFSET(4)] AS weekly_rho_max
FROM pooled AS p
LEFT JOIN weekly AS w USING (variant, market, category);
