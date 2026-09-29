# Phase 1 summary

- Netflix window: 2026-07-05 to 2026-09-20 (12 weeks)
- Pageview range: 2026-06-01 to 2026-09-20 (112 days)
- Titles: 378; matched on Wikidata: 240
- Charted title-market pairs: 641; with an article: 273; dropped: 368

## Checks

- [x] Netflix window has 12 weeks
- [x] Netflix file covers all 6 markets
- [x] Every title in titles.csv charted somewhere
- [x] Kept + dropped pairs = charted pairs
- [x] Every kept pair actually charted in that market
- [x] Pageview rows = kept pairs x days
- [x] No null pageviews

## Wikidata match method

netflix_id: item has a Netflix ID (P1874). label_*: no Netflix ID, matched on exact English label plus type. none: dropped.

| match_method        |   titles |
|:--------------------|---------:|
| netflix_id          |      150 |
| none                |      138 |
| label_unique        |       82 |
| netflix_id_tiebreak |        5 |
| label_tiebreak      |        3 |

## Contested Netflix-ID matches

A newer film or series with the same title exists. A rival overrides the Netflix-ID item only if it is dated within 2 years before the pair's first chart week and has an article in that market's language. Undated rivals never override.

| outcome          |   pairs |   titles |
|:-----------------|--------:|---------:|
| contested_kept   |      32 |       19 |
| resolved_by_date |       4 |        4 |

| title_id   | show_title                 | market   | first_week   | netflix_id_qid   | outcome          | final_qid   | note                                                  |
|:-----------|:---------------------------|:---------|:-------------|:-----------------|:-----------------|:------------|:------------------------------------------------------|
| T015       | The Debt Collector         | BR       | 2026-07-26   | Q56365946        | contested_kept   | Q56365946   | no dated rival within 2 years before first chart week |
| T015       | The Debt Collector         | FR       | 2026-07-26   | Q56365946        | contested_kept   | Q56365946   | no dated rival within 2 years before first chart week |
| T015       | The Debt Collector         | IT       | 2026-07-26   | Q56365946        | contested_kept   | Q56365946   | no dated rival within 2 years before first chart week |
| T015       | The Debt Collector         | JP       | 2026-08-02   | Q56365946        | contested_kept   | Q56365946   | no dated rival within 2 years before first chart week |
| T015       | The Debt Collector         | KR       | 2026-07-26   | Q56365946        | contested_kept   | Q56365946   | no dated rival within 2 years before first chart week |
| T024       | Avatar: The Last Airbender | BR       | 2026-07-05   | Q109608844       | contested_kept   | Q109608844  | no dated rival within 2 years before first chart week |
| T024       | Avatar: The Last Airbender | DE       | 2026-07-05   | Q109608844       | contested_kept   | Q109608844  | no dated rival within 2 years before first chart week |
| T024       | Avatar: The Last Airbender | FR       | 2026-07-05   | Q109608844       | contested_kept   | Q109608844  | no dated rival within 2 years before first chart week |
| T024       | Avatar: The Last Airbender | IT       | 2026-07-05   | Q109608844       | contested_kept   | Q109608844  | no dated rival within 2 years before first chart week |
| T091       | Anora                      | FR       | 2026-09-20   | Q123185887       | contested_kept   | Q123185887  | no dated rival within 2 years before first chart week |
| T091       | Anora                      | IT       | 2026-07-12   | Q123185887       | contested_kept   | Q123185887  | no dated rival within 2 years before first chart week |
| T095       | Breaking In                | DE       | 2026-08-16   | Q4287509         | contested_kept   | Q4287509    | no dated rival within 2 years before first chart week |
| T095       | Breaking In                | JP       | 2026-08-23   | Q4287509         | contested_kept   | Q4287509    | no dated rival within 2 years before first chart week |
| T103       | The Contractor             | FR       | 2026-07-05   | Q2300207         | contested_kept   | Q2300207    | no dated rival within 2 years before first chart week |
| T103       | The Contractor             | IT       | 2026-07-05   | Q2300207         | contested_kept   | Q2300207    | no dated rival within 2 years before first chart week |
| T104       | Angel Eyes                 | FR       | 2026-07-05   | Q531675          | contested_kept   | Q531675     | no dated rival within 2 years before first chart week |
| T104       | Angel Eyes                 | IT       | 2026-07-05   | Q531675          | contested_kept   | Q531675     | no dated rival within 2 years before first chart week |
| T110       | Into the Blue              | JP       | 2026-07-05   | Q1130297         | contested_kept   | Q1130297    | no dated rival within 2 years before first chart week |
| T110       | Into the Blue              | KR       | 2026-07-05   | Q1130297         | contested_kept   | Q1130297    | no dated rival within 2 years before first chart week |
| T111       | The Town                   | FR       | 2026-07-19   | Q725539          | contested_kept   | Q725539     | no dated rival within 2 years before first chart week |
| T111       | The Town                   | IT       | 2026-07-19   | Q725539          | contested_kept   | Q725539     | no dated rival within 2 years before first chart week |
| T116       | The Mentalist              | BR       | 2026-07-19   | Q204228          | contested_kept   | Q204228     | no dated rival within 2 years before first chart week |
| T153       | 13 Minutes                 | BR       | 2026-08-30   | Q18977471        | contested_kept   | Q18977471   | no dated rival within 2 years before first chart week |
| T188       | How to Train Your Dragon   | FR       | 2026-09-13   | Q373096          | resolved_by_date | Q118904382  | rival Q118904382 dated 2025-09-05                     |
| T206       | The Morning After          | FR       | 2026-08-23   | Q1195881         | contested_kept   | Q1195881    | no dated rival within 2 years before first chart week |
| T215       | Ghost Ship                 | DE       | 2026-07-05   | Q1356265         | contested_kept   | Q1356265    | no dated rival within 2 years before first chart week |
| T247       | Turbulence                 | FR       | 2026-08-09   | Q727775          | contested_kept   | Q727775     | no dated rival within 2 years before first chart week |
| T270       | Drop                       | FR       | 2026-08-02   | Q13562077        | resolved_by_date | Q125983478  | rival Q125983478 dated 2025-04-17                     |
| T274       | Someone Like You           | IT       | 2026-08-02   | Q1346535         | contested_kept   | Q1346535    | no dated rival within 2 years before first chart week |
| T283       | Love Hurts                 | FR       | 2026-08-23   | Q2714762         | resolved_by_date | Q125265183  | rival Q125265183 dated 2025-02-07                     |
| T317       | Lovesick                   | FR       | 2026-09-13   | Q18356285        | contested_kept   | Q18356285   | no dated rival within 2 years before first chart week |
| T323       | Siberia                    | BR       | 2026-07-05   | Q30689574        | contested_kept   | Q30689574   | no dated rival within 2 years before first chart week |
| T324       | Silent Night               | JP       | 2026-08-09   | Q85801170        | contested_kept   | Q85801170   | no dated rival within 2 years before first chart week |
| T337       | Collateral Damage          | BR       | 2026-08-23   | Q506605          | contested_kept   | Q506605     | no dated rival within 2 years before first chart week |
| T340       | Dune                       | DE       | 2026-09-13   | Q114819          | contested_kept   | Q114819     | no dated rival within 2 years before first chart week |
| T358       | Wolf Man                   | KR       | 2026-09-06   | Q431873          | resolved_by_date | Q111464581  | rival Q111464581 dated 2025-01-24                     |

Kept pairs by match status:

| match_status     |   pairs |
|:-----------------|--------:|
| ok               |     243 |
| contested_kept   |      26 |
| resolved_by_date |       4 |

## Mapping rate per market

Titles that charted in the market vs titles with an article in that market's language edition.

| market   |   Films charted |   Films w/ article | Films rate   |   TV charted |   TV w/ article | TV rate   |   All charted |   All w/ article | All rate   |
|:---------|----------------:|-------------------:|:-------------|-------------:|----------------:|:----------|--------------:|-----------------:|:-----------|
| DE       |              60 |                 31 | 52%          |           43 |              15 | 35%       |           103 |               46 | 45%        |
| FR       |              73 |                 46 | 63%          |           45 |              22 | 49%       |           118 |               68 | 58%        |
| JP       |              72 |                 18 | 25%          |           39 |              11 | 28%       |           111 |               29 | 26%        |
| BR       |              60 |                 27 | 45%          |           46 |               8 | 17%       |           106 |               35 | 33%        |
| IT       |              63 |                 36 | 57%          |           44 |              17 | 39%       |           107 |               53 | 50%        |
| KR       |              59 |                 26 | 44%          |           37 |              16 | 43%       |            96 |               42 | 44%        |

## Dropped pairs per market

| market   |   matched, no article in that language |   title unmatched on Wikidata |
|:---------|---------------------------------------:|------------------------------:|
| DE       |                                     29 |                            28 |
| FR       |                                     17 |                            33 |
| JP       |                                     33 |                            49 |
| BR       |                                     38 |                            33 |
| IT       |                                     20 |                            34 |
| KR       |                                     20 |                            34 |

## n per market-week: summary (threshold n >= 4)

| market   | Films weeks n>=4   | TV weeks n>=4   |   Films n min |   Films n median |   Films n max |   TV n min |   TV n median |   TV n max |
|:---------|:-------------------|:----------------|--------------:|-----------------:|--------------:|-----------:|--------------:|-----------:|
| DE       | 10 / 12            | 10 / 12         |             2 |                6 |             7 |          3 |           4   |          6 |
| FR       | 12 / 12            | 12 / 12         |             4 |                7 |             9 |          4 |           5.5 |          6 |
| JP       | 2 / 12             | 11 / 12         |             1 |                2 |             4 |          3 |           5   |          7 |
| BR       | 11 / 12            | 1 / 12          |             1 |                5 |             7 |          1 |           2   |          4 |
| IT       | 12 / 12            | 6 / 12          |             4 |                6 |             8 |          1 |           3.5 |          6 |
| KR       | 9 / 12             | 11 / 12         |             3 |                5 |             6 |          3 |           5   |          8 |

## n per market-week, split by Films (F) and TV

Charting titles with an article. Week = Sunday ending the Netflix week.

| week       |   DE F |   DE TV |   FR F |   FR TV |   JP F |   JP TV |   BR F |   BR TV |   IT F |   IT TV |   KR F |   KR TV |
|:-----------|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|
| 2026-07-05 |      7 |       4 |      7 |       5 |      2 |       5 |      1 |       1 |      7 |       4 |      3 |       6 |
| 2026-07-12 |      6 |       5 |      5 |       5 |      1 |       5 |      4 |       1 |      6 |       4 |      6 |       6 |
| 2026-07-19 |      2 |       4 |      5 |       5 |      3 |       3 |      5 |       2 |      6 |       3 |      5 |       7 |
| 2026-07-26 |      3 |       5 |      6 |       6 |      3 |       4 |      5 |       1 |      4 |       4 |      5 |       5 |
| 2026-08-02 |      4 |       3 |      7 |       5 |      2 |       5 |      4 |       2 |      7 |       1 |      5 |       5 |
| 2026-08-09 |      6 |       4 |      9 |       6 |      2 |       7 |      6 |       3 |      8 |       2 |      5 |       6 |
| 2026-08-16 |      5 |       4 |      8 |       6 |      2 |       5 |      4 |       2 |      5 |       2 |      5 |       8 |
| 2026-08-23 |      6 |       6 |      5 |       6 |      2 |       5 |      4 |       4 |      4 |       3 |      5 |       5 |
| 2026-08-30 |      6 |       4 |      7 |       6 |      2 |       5 |      5 |       2 |      6 |       3 |      3 |       5 |
| 2026-09-06 |      7 |       4 |      4 |       4 |      4 |       4 |      7 |       2 |      6 |       4 |      3 |       4 |
| 2026-09-13 |      5 |       4 |      7 |       6 |      4 |       5 |      5 |       1 |      6 |       6 |      4 |       3 |
| 2026-09-20 |      6 |       3 |      9 |       5 |      1 |       6 |      6 |       3 |      6 |       5 |      5 |       5 |
