# Phase 2 summary

## Checks

- [x] Loaded tables match local CSV row counts
- [x] Every pageview week has 7 days
- [x] Missing-week status counts match pandas
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

| table              |   rows |
|:-------------------|-------:|
| agreement_pooled   |     24 |
| agreement_weekly   |    278 |
| article_coverage   |    273 |
| coverage_by_market |     12 |
| discrepancies      |    909 |
| pageviews_weekly   |   4368 |
| ranked             |   1136 |
| timing             |    273 |
| title_market_week  |   1414 |
| title_week_status  |    655 |

## Missing weeks (charting title-weeks with an article)

Only `kept` weeks are ranked. `before_first_view`: week ends before the pair's first recorded pageview. `partial_week`: the first view falls inside the week.

| market   |   before_first_view |   kept |   no_views |   partial_week |
|:---------|--------------------:|-------:|-----------:|---------------:|
| DE       |                  13 |     98 |          0 |              2 |
| FR       |                   9 |    128 |          1 |              6 |
| JP       |                   3 |     82 |          0 |              2 |
| BR       |                   0 |     76 |          3 |              1 |
| IT       |                   8 |     96 |          0 |              8 |
| KR       |                   3 |    111 |          4 |              1 |
| total    |                  36 |    591 |          8 |             20 |

## Coverage: days from first chart week (Monday) to first pageview

Quartiles exclude articles already read before the range began (covered_before_range).

| market   | category   |   pairs |   covered_before_range |   covered_by_chart_start |   appeared_after_chart |   no_views |   days_q1 |   days_median |   days_q3 |
|:---------|:-----------|--------:|-----------------------:|-------------------------:|-----------------------:|-----------:|----------:|--------------:|----------:|
| DE       | Films      |      31 |                     25 |                       30 |                      1 |          0 |       -34 |           -34 |       -14 |
| FR       | Films      |      46 |                     38 |                       40 |                      5 |          1 |       -16 |             8 |        12 |
| JP       | Films      |      18 |                     17 |                       17 |                      1 |          0 |        27 |            27 |        27 |
| BR       | Films      |      27 |                     20 |                       26 |                      1 |          0 |       -77 |           -34 |       -12 |
| IT       | Films      |      36 |                     28 |                       29 |                      7 |          0 |         2 |             3 |         4 |
| KR       | Films      |      26 |                     14 |                       24 |                      2 |          0 |       -83 |           -52 |       -41 |
| DE       | TV         |      15 |                      9 |                       11 |                      4 |          0 |       -14 |             5 |        26 |
| FR       | TV         |      22 |                     13 |                       19 |                      3 |          0 |        -9 |            -8 |         7 |
| JP       | TV         |      11 |                      8 |                        9 |                      2 |          0 |      -103 |             6 |         8 |
| BR       | TV         |       8 |                      7 |                        7 |                      0 |          1 |       nan |           nan |       nan |
| IT       | TV         |      17 |                     10 |                       12 |                      5 |          0 |        -3 |             5 |        40 |
| KR       | TV         |      16 |                     15 |                       15 |                      0 |          1 |       nan |           nan |       nan |

## Sample: agreement per market-category (headline = pooled_rho)

Weekly quartiles cover weeks with n >= 4 only.

| variant             | market   | category   |   pooled_rho |   n_title_weeks |   n_weeks |   n_titles |   weeks_with_rho |   weekly_rho_q1 |   weekly_rho_median |   weekly_rho_q3 |
|:--------------------|:---------|:-----------|-------------:|----------------:|----------:|-----------:|-----------------:|----------------:|--------------------:|----------------:|
| all                 | DE       | Films      |         0.59 |              61 |        12 |         31 |               10 |            0.4  |                0.66 |            0.94 |
| all                 | FR       | Films      |         0.41 |              67 |        12 |         44 |               10 |            0.14 |                0.2  |            0.7  |
| all                 | JP       | Films      |         0.6  |              24 |         9 |         15 |                2 |           -0.4  |               -0.4  |            0.4  |
| all                 | BR       | Films      |         0.19 |              54 |        11 |         27 |               11 |           -0.2  |                0.37 |            0.8  |
| all                 | IT       | Films      |         0.3  |              62 |        11 |         35 |               10 |            0.14 |                0.3  |            0.4  |
| all                 | KR       | Films      |         0.45 |              50 |        12 |         24 |                8 |           -0.1  |                0.1  |            0.6  |
| all                 | DE       | TV         |         0.04 |              37 |        12 |         13 |                3 |            0    |                0.1  |            0.8  |
| all                 | FR       | TV         |         0.7  |              61 |        12 |         21 |               12 |            0.6  |                0.77 |            0.9  |
| all                 | JP       | TV         |         0.2  |              56 |        12 |         11 |               11 |           -0.31 |                0.26 |            0.6  |
| all                 | BR       | TV         |        -0.19 |              18 |         7 |          7 |                1 |            0.6  |                0.6  |            0.6  |
| all                 | IT       | TV         |         0.46 |              31 |        10 |         14 |                3 |            0.3  |                0.5  |            0.8  |
| all                 | KR       | TV         |         0.55 |              61 |        12 |         15 |               10 |            0.2  |                0.5  |            0.83 |
| excl_contested_kept | DE       | Films      |         0.62 |              56 |        12 |         28 |               10 |            0.49 |                0.66 |            0.94 |
| excl_contested_kept | FR       | Films      |         0.38 |              60 |        12 |         38 |                9 |            0.14 |                0.24 |            0.7  |
| excl_contested_kept | JP       | Films      |         0.55 |              22 |         8 |         14 |                2 |           -0.4  |               -0.4  |            0.4  |
| excl_contested_kept | BR       | Films      |         0.16 |              50 |        11 |         25 |                9 |            0.09 |                0.4  |            0.8  |
| excl_contested_kept | IT       | Films      |         0.32 |              56 |        11 |         30 |               10 |            0.21 |                0.37 |            0.49 |
| excl_contested_kept | KR       | Films      |         0.41 |              48 |        11 |         23 |                8 |           -0.1  |                0.1  |            0.6  |
| excl_contested_kept | DE       | TV         |        -0.16 |              33 |        12 |         12 |                2 |            0.1  |                0.1  |            0.8  |
| excl_contested_kept | FR       | TV         |         0.7  |              57 |        12 |         19 |               10 |            0.6  |                0.7  |            0.8  |
| excl_contested_kept | JP       | TV         |         0.2  |              56 |        12 |         11 |               11 |           -0.31 |                0.26 |            0.6  |
| excl_contested_kept | BR       | TV         |         0.17 |               7 |         3 |          6 |                0 |          nan    |              nan    |          nan    |
| excl_contested_kept | IT       | TV         |         0.51 |              26 |         8 |         13 |                3 |            0.3  |                0.5  |            0.8  |
| excl_contested_kept | KR       | TV         |         0.55 |              61 |        12 |         15 |               10 |            0.2  |                0.5  |            0.83 |

## Sample: discrepancy rate (variant all, n >= 4)

|                 |   evaluated |   flagged |   rate |
|:----------------|------------:|----------:|-------:|
| ('DE', 'Films') |          56 |         7 |   0.12 |
| ('DE', 'TV')    |          13 |         5 |   0.38 |
| ('FR', 'Films') |          62 |        17 |   0.27 |
| ('FR', 'TV')    |          61 |         7 |   0.11 |
| ('JP', 'Films') |           8 |         3 |   0.38 |
| ('JP', 'TV')    |          53 |        20 |   0.38 |
| ('BR', 'Films') |          54 |        14 |   0.26 |
| ('BR', 'TV')    |           4 |         0 |   0    |
| ('IT', 'Films') |          59 |        18 |   0.31 |
| ('IT', 'TV')    |          14 |         5 |   0.36 |
| ('KR', 'Films') |          39 |        17 |   0.44 |
| ('KR', 'TV')    |          56 |         9 |   0.16 |

## Sample: largest discrepancies

| market   | category   | week_end   | show_title                       |   n |   netflix_rank_in_set |   pageview_rank_in_set |   views | direction       |
|:---------|:-----------|:-----------|:---------------------------------|----:|----------------------:|-----------------------:|--------:|:----------------|
| BR       | Films      | 2026-08-09 | The Last House                   |   6 |                     1 |                      6 |       0 | netflix_ahead   |
| BR       | Films      | 2026-08-16 | The Last House                   |   4 |                     1 |                      4 |     373 | netflix_ahead   |
| BR       | Films      | 2026-08-30 | The Last House                   |   4 |                     4 |                      1 |     910 | attention_ahead |
| BR       | Films      | 2026-08-16 | Spider-Man: Far from Home        |   4 |                     4 |                      1 |    4323 | attention_ahead |
| JP       | TV         | 2026-07-12 | Human Vapor                      |   5 |                     1 |                      5 |    6472 | netflix_ahead   |
| IT       | Films      | 2026-07-19 | Journey 2: The Mysterious Island |   6 |                     1 |                      6 |    1733 | netflix_ahead   |
| BR       | Films      | 2026-08-30 | 13 Minutes                       |   4 |                     1 |                      4 |       2 | netflix_ahead   |
| KR       | TV         | 2026-08-09 | I am Solo                        |   6 |                     1 |                      6 |     532 | netflix_ahead   |

## Sample: timing (days from first chart week's Monday to pageview peak)

|                            |   count |
|:---------------------------|--------:|
| pairs                      |     273 |
| left_censored              |      29 |
| peak_at_range_edge         |      15 |
| no_views                   |       3 |
| article_after_chart        |      31 |
| usable (none of the above) |     208 |

|                 |   pairs |   median |   q1 |   q3 |
|:----------------|--------:|---------:|-----:|-----:|
| ('DE', 'Films') |      27 |      6   |  1   |  6   |
| ('DE', 'TV')    |       9 |      6   |  3   |  6   |
| ('FR', 'Films') |      38 |      2   | -1   |  5.8 |
| ('FR', 'TV')    |      14 |      6   |  3.5 |  6   |
| ('JP', 'Films') |      16 |      3   | -1   |  5.2 |
| ('JP', 'TV')    |       6 |      8   |  3.2 | 16.5 |
| ('BR', 'Films') |      24 |      6   | -1   |  6   |
| ('BR', 'TV')    |       6 |      4   |  0.8 |  5.8 |
| ('IT', 'Films') |      26 |      3   | -1   |  5.8 |
| ('IT', 'TV')    |      10 |      3.5 |  2   |  5.5 |
| ('KR', 'Films') |      22 |      3.5 |  0.2 |  5   |
| ('KR', 'TV')    |      10 |      5.5 |  5   |  6   |
