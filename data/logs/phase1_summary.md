# Phase 1 summary

- Netflix window: 2026-07-05 to 2026-09-20 (12 weeks)
- Pageview range: 2026-06-01 to 2026-09-20 (112 days)
- Titles: 378; matched on Wikidata: 238
- Charted title-market pairs: 641; with an article: 260; dropped: 381

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
| netflix_id          |      147 |
| none                |      140 |
| label_unique        |       81 |
| netflix_id_tiebreak |        7 |
| label_tiebreak      |        3 |

Contested Netflix-ID matches (a newer same-type namesake exists): 22 titles, 25 title-market pairs with an article.

| title_id   | show_title               | category   | qid        | newer_rivals                                       |
|:-----------|:-------------------------|:-----------|:-----------|:---------------------------------------------------|
| T015       | The Debt Collector       | Films      | Q56365946  | Q140724430                                         |
| T091       | Anora                    | Films      | Q123185887 | Q55604021                                          |
| T095       | Breaking In              | Films      | Q4287509   | Q39075152                                          |
| T103       | The Contractor           | Films      | Q2300207   | Q15129302 Q73549328                                |
| T104       | Angel Eyes               | Films      | Q531675    | Q79999129                                          |
| T110       | Into the Blue            | Films      | Q1130297   | Q111738314 Q19368817                               |
| T111       | The Town                 | Films      | Q725539    | Q110748481 Q97168270                               |
| T116       | The Mentalist            | TV         | Q204228    | Q30474612                                          |
| T153       | 13 Minutes               | Films      | Q18977471  | Q110585233                                         |
| T188       | How to Train Your Dragon | Films      | Q373096    | Q118904382                                         |
| T206       | The Morning After        | Films      | Q1195881   | Q108881445 Q132860832 Q98416496                    |
| T215       | Ghost Ship               | Films      | Q1356265   | Q56692143 Q65598517 Q97212591                      |
| T247       | Turbulence               | Films      | Q727775    | Q137384638 Q7854768 Q7854769 Q97104712             |
| T270       | Drop                     | Films      | Q13562077  | Q125983478                                         |
| T274       | Someone Like You         | Films      | Q1346535   | Q109457856 Q125883233 Q20729515 Q3475092 Q57835558 |
| T283       | Love Hurts               | Films      | Q2714762   | Q125265183                                         |
| T317       | Lovesick                 | TV         | Q134646503 | Q139603851                                         |
| T323       | Siberia                  | Films      | Q30689574  | Q48919934 Q83954889                                |
| T324       | Silent Night             | Films      | Q85801170  | Q112078051                                         |
| T337       | Collateral Damage        | Films      | Q506605    | Q66069483                                          |
| T340       | Dune                     | Films      | Q114819    | Q20972530 Q60834962 Q65212698                      |
| T358       | Wolf Man                 | Films      | Q431873    | Q111464581                                         |

## Mapping rate per market

Titles that charted in the market vs titles with an article in that market's language edition.

| market   |   Films charted |   Films w/ article | Films rate   |   TV charted |   TV w/ article | TV rate   |   All charted |   All w/ article | All rate   |
|:---------|----------------:|-------------------:|:-------------|-------------:|----------------:|:----------|--------------:|-----------------:|:-----------|
| DE       |              60 |                 31 | 52%          |           43 |              11 | 26%       |           103 |               42 | 41%        |
| FR       |              73 |                 46 | 63%          |           45 |              18 | 40%       |           118 |               64 | 54%        |
| JP       |              72 |                 18 | 25%          |           39 |              11 | 28%       |           111 |               29 | 26%        |
| BR       |              60 |                 27 | 45%          |           46 |               6 | 13%       |           106 |               33 | 31%        |
| IT       |              63 |                 36 | 57%          |           44 |              14 | 32%       |           107 |               50 | 47%        |
| KR       |              59 |                 26 | 44%          |           37 |              16 | 43%       |            96 |               42 | 44%        |

## Dropped pairs per market

| market   |   matched, no article in that language |   title unmatched on Wikidata |
|:---------|---------------------------------------:|------------------------------:|
| DE       |                                     31 |                            30 |
| FR       |                                     20 |                            34 |
| JP       |                                     33 |                            49 |
| BR       |                                     39 |                            34 |
| IT       |                                     22 |                            35 |
| KR       |                                     20 |                            34 |

## n per market-week: summary (threshold n >= 4)

| market   | Films weeks n>=4   | TV weeks n>=4   |   Films n min |   Films n median |   Films n max |   TV n min |   TV n median |   TV n max |
|:---------|:-------------------|:----------------|--------------:|-----------------:|--------------:|-----------:|--------------:|-----------:|
| DE       | 10 / 12            | 3 / 12          |             2 |                6 |             7 |          2 |           3   |          5 |
| FR       | 12 / 12            | 11 / 12         |             4 |                7 |             9 |          3 |           4.5 |          6 |
| JP       | 2 / 12             | 11 / 12         |             1 |                2 |             5 |          3 |           5   |          7 |
| BR       | 11 / 12            | 0 / 12          |             1 |                5 |             7 |          0 |           2   |          3 |
| IT       | 12 / 12            | 3 / 12          |             4 |                6 |             8 |          1 |           2.5 |          5 |
| KR       | 9 / 12             | 11 / 12         |             3 |                5 |             6 |          3 |           5   |          8 |

## n per market-week, split by Films (F) and TV

Charting titles with an article. Week = Sunday ending the Netflix week.

| week       |   DE F |   DE TV |   FR F |   FR TV |   JP F |   JP TV |   BR F |   BR TV |   IT F |   IT TV |   KR F |   KR TV |
|:-----------|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|
| 2026-07-05 |      7 |       3 |      7 |       4 |      2 |       5 |      1 |       0 |      7 |       3 |      3 |       6 |
| 2026-07-12 |      6 |       3 |      5 |       4 |      1 |       5 |      4 |       0 |      6 |       3 |      6 |       6 |
| 2026-07-19 |      2 |       2 |      5 |       4 |      2 |       3 |      5 |       1 |      6 |       2 |      5 |       7 |
| 2026-07-26 |      3 |       3 |      6 |       6 |      3 |       4 |      5 |       1 |      4 |       4 |      5 |       5 |
| 2026-08-02 |      4 |       2 |      7 |       5 |      2 |       5 |      4 |       2 |      7 |       1 |      5 |       5 |
| 2026-08-09 |      6 |       4 |      9 |       6 |      2 |       7 |      6 |       3 |      8 |       2 |      5 |       6 |
| 2026-08-16 |      5 |       4 |      8 |       6 |      2 |       5 |      4 |       2 |      5 |       2 |      5 |       8 |
| 2026-08-23 |      6 |       5 |      5 |       5 |      3 |       5 |      4 |       3 |      4 |       2 |      5 |       5 |
| 2026-08-30 |      6 |       3 |      7 |       5 |      3 |       5 |      5 |       2 |      6 |       2 |      3 |       5 |
| 2026-09-06 |      7 |       3 |      4 |       3 |      5 |       4 |      7 |       2 |      6 |       3 |      3 |       4 |
| 2026-09-13 |      5 |       3 |      7 |       4 |      4 |       5 |      5 |       1 |      6 |       5 |      4 |       3 |
| 2026-09-20 |      6 |       2 |      9 |       4 |      1 |       6 |      6 |       3 |      6 |       4 |      5 |       5 |
