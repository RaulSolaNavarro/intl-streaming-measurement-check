# Phase 3 analysis

Bootstrap: 2000 resamples of weeks, seed 20260928. Point estimates match BigQuery (max diff 7.8e-16). Low confidence = fewer than 30 title-weeks.

## 1. Agreement (pooled Spearman, 95% CI)

| variant             | market   | category   |   pooled_rho |   ci_low |   ci_high |   n_title_weeks |   n_weeks | low_confidence   | ci_excludes_zero   |   boot_skipped |   weeks_with_rho |   weekly_rho_q1 |   weekly_rho_median |   weekly_rho_q3 |
|:--------------------|:---------|:-----------|-------------:|---------:|----------:|----------------:|----------:|:-----------------|:-------------------|---------------:|-----------------:|----------------:|--------------------:|----------------:|
| all                 | DE       | Films      |         0.59 |     0.3  |      0.82 |              61 |        12 | False            | True               |              0 |               10 |            0.4  |                0.66 |            0.94 |
| all                 | FR       | Films      |         0.41 |     0.2  |      0.64 |              67 |        12 | False            | True               |              0 |               10 |            0.14 |                0.2  |            0.7  |
| all                 | JP       | Films      |         0.6  |     0.18 |      1    |              24 |         9 | True             | True               |              0 |                2 |           -0.4  |               -0.4  |            0.4  |
| all                 | BR       | Films      |         0.19 |    -0.16 |      0.51 |              54 |        11 | False            | False              |              0 |               11 |           -0.2  |                0.37 |            0.8  |
| all                 | IT       | Films      |         0.3  |     0.14 |      0.44 |              62 |        11 | False            | True               |              0 |               10 |            0.14 |                0.3  |            0.4  |
| all                 | KR       | Films      |         0.45 |     0.23 |      0.69 |              50 |        12 | False            | True               |              0 |                8 |           -0.1  |                0.1  |            0.6  |
| all                 | DE       | TV         |         0.04 |    -0.37 |      0.42 |              37 |        12 | False            | False              |              0 |                3 |            0    |                0.1  |            0.8  |
| all                 | FR       | TV         |         0.7  |     0.53 |      0.85 |              61 |        12 | False            | True               |              0 |               12 |            0.6  |                0.77 |            0.9  |
| all                 | JP       | TV         |         0.2  |    -0.03 |      0.43 |              56 |        12 | False            | False              |              0 |               11 |           -0.31 |                0.26 |            0.6  |
| all                 | BR       | TV         |        -0.19 |    -0.79 |      0.38 |              18 |         7 | True             | False              |              0 |                1 |            0.6  |                0.6  |            0.6  |
| all                 | IT       | TV         |         0.46 |     0.06 |      0.82 |              31 |        10 | False            | True               |              0 |                3 |            0.3  |                0.5  |            0.8  |
| all                 | KR       | TV         |         0.55 |     0.35 |      0.74 |              61 |        12 | False            | True               |              0 |               10 |            0.2  |                0.5  |            0.83 |
| excl_contested_kept | DE       | Films      |         0.62 |     0.34 |      0.84 |              56 |        12 | False            | True               |              0 |               10 |            0.49 |                0.66 |            0.94 |
| excl_contested_kept | FR       | Films      |         0.38 |     0.11 |      0.64 |              60 |        12 | False            | True               |              0 |                9 |            0.14 |                0.24 |            0.7  |
| excl_contested_kept | JP       | Films      |         0.55 |     0.07 |      0.92 |              22 |         8 | True             | True               |              0 |                2 |           -0.4  |               -0.4  |            0.4  |
| excl_contested_kept | BR       | Films      |         0.16 |    -0.23 |      0.48 |              50 |        11 | False            | False              |              0 |                9 |            0.09 |                0.4  |            0.8  |
| excl_contested_kept | IT       | Films      |         0.32 |     0.08 |      0.5  |              56 |        11 | False            | True               |              0 |               10 |            0.21 |                0.37 |            0.49 |
| excl_contested_kept | KR       | Films      |         0.41 |     0.18 |      0.64 |              48 |        11 | False            | True               |              0 |                8 |           -0.1  |                0.1  |            0.6  |
| excl_contested_kept | DE       | TV         |        -0.16 |    -0.58 |      0.28 |              33 |        12 | False            | False              |              0 |                2 |            0.1  |                0.1  |            0.8  |
| excl_contested_kept | FR       | TV         |         0.7  |     0.53 |      0.85 |              57 |        12 | False            | True               |              0 |               10 |            0.6  |                0.7  |            0.8  |
| excl_contested_kept | JP       | TV         |         0.2  |    -0.03 |      0.42 |              56 |        12 | False            | False              |              0 |               11 |           -0.31 |                0.26 |            0.6  |
| excl_contested_kept | BR       | TV         |         0.17 |    -1    |      1    |               7 |         3 | True             | False              |              0 |                0 |          nan    |              nan    |          nan    |
| excl_contested_kept | IT       | TV         |         0.51 |     0.01 |      0.86 |              26 |         8 | True             | True               |              0 |                3 |            0.3  |                0.5  |            0.8  |
| excl_contested_kept | KR       | TV         |         0.55 |     0.35 |      0.73 |              61 |        12 | False            | True               |              0 |               10 |            0.2  |                0.5  |            0.83 |

## 2a. Discrepancy rate (n >= 4 weeks)

| market   | category   |   evaluated |   flagged |   netflix_ahead |   attention_ahead |   rate |
|:---------|:-----------|------------:|----------:|----------------:|------------------:|-------:|
| DE       | Films      |          56 |         7 |               4 |                 3 |   0.12 |
| FR       | Films      |          62 |        17 |               8 |                 9 |   0.27 |
| JP       | Films      |           8 |         3 |               2 |                 1 |   0.38 |
| BR       | Films      |          54 |        14 |               8 |                 6 |   0.26 |
| IT       | Films      |          59 |        18 |               9 |                 9 |   0.31 |
| KR       | Films      |          39 |        17 |               9 |                 8 |   0.44 |
| DE       | TV         |          13 |         5 |               3 |                 2 |   0.38 |
| FR       | TV         |          61 |         7 |               5 |                 2 |   0.11 |
| JP       | TV         |          53 |        20 |              10 |                10 |   0.38 |
| BR       | TV         |           4 |         0 |               0 |                 0 |   0    |
| IT       | TV         |          14 |         5 |               2 |                 3 |   0.36 |
| KR       | TV         |          56 |         9 |               6 |                 3 |   0.16 |

## 2b. Titles flagged in 2+ weeks

| market   | category   | title_id   | show_title                   | direction       |   weeks_flagged |
|:---------|:-----------|:-----------|:-----------------------------|:----------------|----------------:|
| JP       | TV         | T115       | Vivant                       | attention_ahead |               8 |
| JP       | TV         | T074       | Badly in Love                | netflix_ahead   |               6 |
| KR       | TV         | T121       | I am Solo                    | netflix_ahead   |               4 |
| KR       | Films      | T036       | Spider-Man: Far from Home    | attention_ahead |               4 |
| KR       | Films      | T127       | Wild Sing                    | netflix_ahead   |               4 |
| FR       | TV         | T017       | My Life With the Walter Boys | netflix_ahead   |               3 |
| JP       | TV         | T076       | Human Vapor                  | netflix_ahead   |               3 |
| BR       | Films      | T002       | The Last House               | netflix_ahead   |               2 |
| BR       | Films      | T153       | 13 Minutes                   | netflix_ahead   |               2 |
| DE       | Films      | T215       | Ghost Ship                   | attention_ahead |               2 |
| IT       | TV         | T063       | Fauda                        | attention_ahead |               2 |
| IT       | Films      | T128       | Buen Camino                  | attention_ahead |               2 |
| IT       | Films      | T059       | The Little Things            | netflix_ahead   |               2 |
| IT       | Films      | T002       | The Last House               | attention_ahead |               2 |
| FR       | Films      | T228       | Seven                        | attention_ahead |               2 |
| FR       | Films      | T056       | Spider-Man: Homecoming       | attention_ahead |               2 |
| KR       | Films      | T161       | People and Meat              | netflix_ahead   |               2 |
| KR       | TV         | T039       | The East Palace              | netflix_ahead   |               2 |

## 2c. Signed rank gap by origin (positive = pageviews rank the title higher than Netflix; CI resamples titles)

| market   | origin   |   title_weeks |   titles |   mean_signed_gap |   ci_low |   ci_high |
|:---------|:---------|--------------:|---------:|------------------:|---------:|----------:|
| DE       | domestic |            21 |        9 |             -0.33 |    -0.61 |     -0.05 |
| DE       | foreign  |            77 |       35 |              0.09 |    -0.03 |      0.21 |
| FR       | domestic |            23 |       12 |             -0.02 |    -0.21 |      0.15 |
| FR       | foreign  |           104 |       52 |              0    |    -0.08 |      0.09 |
| FR       | unknown  |             1 |        1 |              0    |   nan    |    nan    |
| JP       | domestic |            60 |       13 |              0.02 |    -0.27 |      0.31 |
| JP       | foreign  |            20 |       13 |             -0.05 |    -0.18 |      0.07 |
| BR       | domestic |             7 |        3 |              0.02 |    -0.25 |      0.67 |
| BR       | foreign  |            64 |       30 |             -0    |    -0.2  |      0.17 |
| BR       | unknown  |             1 |        1 |              0    |   nan    |    nan    |
| IT       | domestic |            14 |        8 |              0.29 |     0.03 |      0.49 |
| IT       | foreign  |            79 |       41 |             -0.05 |    -0.17 |      0.05 |
| KR       | domestic |            84 |       23 |             -0.05 |    -0.19 |      0.08 |
| KR       | foreign  |            27 |       16 |              0.15 |    -0.01 |      0.3  |
| ALL      | domestic |           209 |       67 |             -0.03 |    -0.15 |      0.08 |
| ALL      | foreign  |           371 |      122 |              0.02 |    -0.04 |      0.07 |
| ALL      | unknown  |             2 |        1 |              0    |   nan    |    nan    |

## 3. Timing: days from first chart Monday to pageview peak

| flag                |   pairs |
|:--------------------|--------:|
| left_censored       |      29 |
| no_views            |       3 |
| peak_at_range_edge  |      15 |
| article_after_chart |      31 |
| usable              |     208 |

| market   | category   |   pairs |   median |    q1 |    q3 |   share_before_chart |   share_in_first_week |   share_later |
|:---------|:-----------|--------:|---------:|------:|------:|---------------------:|----------------------:|--------------:|
| DE       | Films      |      27 |      6   |  1    |  6    |                 0.19 |                  0.7  |          0.11 |
| FR       | Films      |      38 |      2   | -1    |  5.75 |                 0.37 |                  0.53 |          0.11 |
| JP       | Films      |      16 |      3   | -1    |  5.25 |                 0.31 |                  0.62 |          0.06 |
| BR       | Films      |      24 |      6   | -1    |  6    |                 0.29 |                  0.58 |          0.12 |
| IT       | Films      |      26 |      3   | -1    |  5.75 |                 0.35 |                  0.54 |          0.12 |
| KR       | Films      |      22 |      3.5 |  0.25 |  5    |                 0.23 |                  0.68 |          0.09 |
| DE       | TV         |       9 |      6   |  3    |  6    |                 0.22 |                  0.67 |          0.11 |
| FR       | TV         |      14 |      6   |  3.5  |  6    |                 0.14 |                  0.64 |          0.21 |
| JP       | TV         |       6 |      8   |  3.25 | 16.5  |                 0.17 |                  0.33 |          0.5  |
| BR       | TV         |       6 |      4   |  0.75 |  5.75 |                 0.17 |                  0.67 |          0.17 |
| IT       | TV         |      10 |      3.5 |  2    |  5.5  |                 0    |                  0.9  |          0.1  |
| KR       | TV         |      10 |      5.5 |  5    |  6    |                 0.1  |                  0.7  |          0.2  |

## 4. Coverage: days from first chart Monday to first pageview

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
