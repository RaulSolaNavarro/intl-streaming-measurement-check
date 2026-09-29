-- 08_discrepancies
-- Title-market-weeks where Netflix rank and pageview rank disagree strongly.
--
-- Definition: |netflix_rank_in_set - pageview_rank_in_set| / (n - 1) >= 0.5,
-- i.e. the two sources place the title at least half the set apart. Only
-- evaluated where n >= 4; with smaller sets a "half the list" gap is one or
-- two positions and mostly noise.
--
-- direction:
--   netflix_ahead    Netflix ranks the title higher than its pageviews do
--                    (watched more than it is looked up)
--   attention_ahead  pageviews rank it higher than Netflix does
--                    (looked up more than it is watched)
-- Every evaluated row is kept, with is_discrepancy as the flag, so rates can
-- be computed per market.

CREATE OR REPLACE TABLE `intl-streaming-measurement.streaming_measurement.discrepancies` AS
SELECT
  variant, market, category, week_end, title_id, show_title, article, match_status,
  n,
  netflix_rank, netflix_rank_in_set, views, pageview_rank_in_set,
  netflix_rank_in_set - pageview_rank_in_set                        AS rank_gap,
  ABS(netflix_rank_in_set - pageview_rank_in_set) / (n - 1)         AS norm_gap,
  ABS(netflix_rank_in_set - pageview_rank_in_set) / (n - 1) >= 0.5  AS is_discrepancy,
  CASE
    WHEN netflix_rank_in_set < pageview_rank_in_set THEN 'netflix_ahead'
    WHEN netflix_rank_in_set > pageview_rank_in_set THEN 'attention_ahead'
    ELSE 'same'
  END                                                               AS direction
FROM `intl-streaming-measurement.streaming_measurement.ranked`
WHERE n >= 4;
