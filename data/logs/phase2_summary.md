# Phase 2 summary

## Checks

- [x] Loaded tables match local CSV row counts
- [x] Every pageview week has 7 days
- [x] Weekly rho: same market-weeks in pandas and BigQuery
- [x] Weekly rho matches pandas (max diff < 1e-9)
- [x] Pooled rho matches pandas (max diff < 1e-9)
- [x] Weekly views = sum of daily (T103 FR 2026-08-02)

## Loaded tables (BigQuery vs local CSV)

| table             |   bigquery_rows |   local_rows |
|:------------------|----------------:|-------------:|
| netflix_top10     |            1440 |         1440 |
| titles            |             378 |          378 |
| title_markets     |             641 |          641 |
| title_article_map |             273 |          273 |
| pageviews_daily   |           30576 |        30576 |
| contested_pairs   |              36 |           36 |
| dropped_pairs     |             368 |          368 |

## Result tables

| table             |   rows |
|:------------------|-------:|
| agreement_pooled  |     24 |
| agreement_weekly  |    283 |
| discrepancies     |   1092 |
| pageviews_weekly  |   4368 |
| ranked            |   1259 |
| timing            |    273 |
| title_market_week |   1414 |

## Sample: agreement per market-category (headline = pooled_rho)

Weekly quartiles cover weeks with n >= 4 only.

| variant             | market   | category   |   pooled_rho |   n_title_weeks |   n_weeks |   n_titles |   weeks_with_rho |   weekly_rho_q1 |   weekly_rho_median |   weekly_rho_q3 |
|:--------------------|:---------|:-----------|-------------:|----------------:|----------:|-----------:|-----------------:|----------------:|--------------------:|----------------:|
| all                 | DE       | Films      |         0.53 |              63 |        12 |         31 |               10 |            0.39 |                0.66 |            0.9  |
| all                 | FR       | Films      |         0.29 |              79 |        12 |         46 |               12 |           -0.07 |                0    |            0.8  |
| all                 | JP       | Films      |         0.44 |              26 |        10 |         17 |                2 |           -0.4  |               -0.4  |            0.4  |
| all                 | BR       | Films      |         0.27 |              55 |        11 |         27 |               11 |            0    |                0.37 |            0.8  |
| all                 | IT       | Films      |         0.35 |              71 |        12 |         36 |               12 |            0.14 |                0.4  |            0.6  |
| all                 | KR       | Films      |         0.36 |              54 |        12 |         26 |                9 |            0.09 |                0.2  |            0.6  |
| all                 | DE       | TV         |         0.02 |              50 |        12 |         15 |               10 |           -0.21 |               -0.11 |            0.2  |
| all                 | FR       | TV         |         0.66 |              65 |        12 |         22 |               12 |            0.6  |                0.7  |            0.8  |
| all                 | JP       | TV         |         0.19 |              59 |        12 |         11 |               11 |           -0.31 |                0.2  |            0.6  |
| all                 | BR       | TV         |        -0.29 |              20 |         8 |          8 |                1 |            0.6  |                0.6  |            0.6  |
| all                 | IT       | TV         |         0.51 |              40 |        11 |         17 |                6 |            0.14 |                0.2  |            0.63 |
| all                 | KR       | TV         |         0.48 |              65 |        12 |         16 |               11 |            0.2  |                0.5  |            0.75 |
| excl_contested_kept | DE       | Films      |         0.57 |              58 |        12 |         28 |               10 |            0.49 |                0.66 |            0.86 |
| excl_contested_kept | FR       | Films      |         0.29 |              72 |        12 |         40 |               12 |           -0.06 |                0.1  |            0.8  |
| excl_contested_kept | JP       | Films      |         0.55 |              22 |         8 |         14 |                2 |           -0.4  |               -0.4  |            0.4  |
| excl_contested_kept | BR       | Films      |         0.25 |              51 |        11 |         25 |               10 |            0.09 |                0.37 |            0.8  |
| excl_contested_kept | IT       | Films      |         0.35 |              63 |        12 |         30 |               11 |            0.14 |                0.48 |            0.6  |
| excl_contested_kept | KR       | Films      |         0.4  |              53 |        12 |         25 |                9 |            0.09 |                0.2  |            0.6  |
| excl_contested_kept | DE       | TV         |        -0.03 |              46 |        12 |         14 |                8 |           -0.11 |                0.03 |            0.21 |
| excl_contested_kept | FR       | TV         |         0.65 |              61 |        12 |         20 |               12 |            0.49 |                0.7  |            0.8  |
| excl_contested_kept | JP       | TV         |         0.19 |              59 |        12 |         11 |               11 |           -0.31 |                0.2  |            0.6  |
| excl_contested_kept | BR       | TV         |         0.17 |               7 |         3 |          6 |                0 |          nan    |              nan    |          nan    |
| excl_contested_kept | IT       | TV         |         0.56 |              37 |        11 |         16 |                4 |            0.14 |                0.3  |            0.63 |
| excl_contested_kept | KR       | TV         |         0.48 |              65 |        12 |         16 |               11 |            0.2  |                0.5  |            0.75 |

## Sample: discrepancy rate (variant all, n >= 4)

|                 |   evaluated |   flagged |   rate |
|:----------------|------------:|----------:|-------:|
| ('DE', 'Films') |          58 |         7 |   0.12 |
| ('DE', 'TV')    |          44 |        18 |   0.41 |
| ('FR', 'Films') |          79 |        23 |   0.29 |
| ('FR', 'TV')    |          65 |         9 |   0.14 |
| ('JP', 'Films') |           8 |         3 |   0.38 |
| ('JP', 'TV')    |          56 |        24 |   0.43 |
| ('BR', 'Films') |          55 |        14 |   0.25 |
| ('BR', 'TV')    |           4 |         0 |   0    |
| ('IT', 'Films') |          71 |        15 |   0.21 |
| ('IT', 'TV')    |          27 |         9 |   0.33 |
| ('KR', 'Films') |          45 |        17 |   0.38 |
| ('KR', 'TV')    |          62 |        12 |   0.19 |

## Sample: largest discrepancies

| market   | category   | week_end   | show_title                       |   n |   netflix_rank_in_set |   pageview_rank_in_set |   views | direction     |
|:---------|:-----------|:-----------|:---------------------------------|----:|----------------------:|-----------------------:|--------:|:--------------|
| BR       | Films      | 2026-08-09 | The Last House                   |   6 |                     1 |                      6 |       0 | netflix_ahead |
| IT       | Films      | 2026-07-19 | Journey 2: The Mysterious Island |   6 |                     1 |                      6 |    1733 | netflix_ahead |
| KR       | TV         | 2026-08-23 | I am Solo                        |   5 |                     1 |                      5 |     484 | netflix_ahead |
| BR       | Films      | 2026-08-16 | The Last House                   |   4 |                     1 |                      4 |     373 | netflix_ahead |
| JP       | TV         | 2026-07-12 | Human Vapor                      |   5 |                     1 |                      5 |    6472 | netflix_ahead |
| KR       | TV         | 2026-08-09 | I am Solo                        |   6 |                     1 |                      6 |     532 | netflix_ahead |
| JP       | TV         | 2026-09-20 | Plastic Beauty                   |   6 |                     1 |                      6 |     420 | netflix_ahead |
| DE       | TV         | 2026-07-12 | I Will Find You                  |   5 |                     1 |                      5 |       0 | netflix_ahead |

## Sample: timing (days from first chart week's Monday to pageview peak)

|                    |   count |
|:-------------------|--------:|
| pairs              |     273 |
| left_censored      |      29 |
| peak_at_range_edge |      15 |
| no_views           |       3 |
| usable             |     231 |

|                 |   pairs |   median |   q1 |   q3 |
|:----------------|--------:|---------:|-----:|-----:|
| ('DE', 'Films') |      28 |      6   |  1   |  6   |
| ('DE', 'TV')    |      12 |      6   |  5.2 | 12   |
| ('FR', 'Films') |      42 |      3   | -1   |  6   |
| ('FR', 'TV')    |      15 |      6   |  4   |  7   |
| ('JP', 'Films') |      17 |      4   | -1   |  6   |
| ('JP', 'TV')    |       7 |     12   |  3.5 | 22.5 |
| ('BR', 'Films') |      25 |      6   | -1   |  6   |
| ('BR', 'TV')    |       6 |      4   |  0.8 |  5.8 |
| ('IT', 'Films') |      33 |      5   | -1   |  6   |
| ('IT', 'TV')    |      12 |      4   |  2   |  6   |
| ('KR', 'Films') |      24 |      4   |  0.8 |  5   |
| ('KR', 'TV')    |      10 |      5.5 |  5   |  6   |
