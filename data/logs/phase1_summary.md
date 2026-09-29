# Phase 1 summary

- Netflix window: 2026-07-05 to 2026-09-20 (12 weeks)
- Pageview range: 2026-06-01 to 2026-09-20 (112 days)
- Titles selected: 20; matched on Wikidata: 15
- Title-market pairs kept: 45; dropped: 75

## Checks

- [x] Netflix window has 12 weeks
- [x] Netflix file covers all 6 markets
- [x] At most 20 titles selected
- [x] Every title charted in >= 3 markets
- [x] Kept + dropped pairs = titles x 6
- [x] Pageview rows = pairs x days
- [x] No null pageviews

## Titles

| title_id   | show_title                            | category   |   n_markets | markets           | qid        | result                                                                                    | markets_with_article   |
|:-----------|:--------------------------------------|:-----------|------------:|:------------------|:-----------|:------------------------------------------------------------------------------------------|:-----------------------|
| T01        | Agent Kim Reactivated                 | TV         |           6 | BR,DE,FR,IT,JP,KR | Q139553270 | unique match                                                                              | DE,FR,IT,KR            |
| T02        | The Last House                        | Films      |           6 | BR,DE,FR,IT,JP,KR | Q129165193 | unique match                                                                              | DE,FR,BR,IT            |
| T03        | The Whisper Man                       | Films      |           6 | BR,DE,FR,IT,JP,KR | Q133852597 | unique match                                                                              | DE,FR,BR,IT,KR         |
| T04        | Elize: Shadows of a Woman             | Films      |           6 | BR,DE,FR,IT,JP,KR | Q140524489 | unique match                                                                              | FR,BR                  |
| T05        | Enola Holmes 3                        | Films      |           6 | BR,DE,FR,IT,JP,KR | Q133876041 | unique match                                                                              | FR,JP,IT,KR            |
| T06        | Facing El Chapo                       | Films      |           6 | BR,DE,FR,IT,JP,KR |            | no Wikidata item with this exact English label                                            |                        |
| T07        | Grand Theft Auto VI: An Extended Look | Films      |           6 | BR,DE,FR,IT,JP,KR | Q141163179 | unique match                                                                              |                        |
| T08        | Anacondas: Trail of Blood             | Films      |           6 | BR,DE,FR,IT,JP,KR | Q716759    | unique match                                                                              | DE,FR,JP,BR,IT         |
| T09        | I Will Find You                       | TV         |           5 | BR,DE,FR,IT,KR    | Q134412018 | unique match                                                                              | DE,FR                  |
| T10        | 72 HOURS                              | Films      |           5 | BR,DE,FR,IT,JP    | Q136339220 | date tie-break among 3 candidates (Q136339220, Q123421847, Q133852731)                    | FR,IT,KR               |
| T11        | The Secret Woman                      | Films      |           5 | BR,DE,FR,IT,KR    | Q140419850 | date tie-break among 2 candidates (Q27590455, Q140419850)                                 | FR                     |
| T12        | Elite Force                           | TV         |           5 | BR,DE,FR,IT,KR    | Q133868511 | unique match                                                                              | FR                     |
| T13        | Desire                                | Films      |           5 | BR,DE,FR,IT,KR    |            | 7 candidates; closest (Q60873103) is 9 years from the window, likely an older namesake    |                        |
| T14        | Our Sticky Love                       | TV         |           5 | BR,FR,IT,JP,KR    | Q137835829 | unique match                                                                              | DE,FR,IT,KR            |
| T15        | The Debt Collector                    | Films      |           5 | BR,FR,IT,JP,KR    |            | 3 candidates; undated item(s) Q140724430 could be the right one, tie not safely breakable |                        |
| T16        | Death on the Nile                     | Films      |           5 | DE,FR,IT,JP,KR    |            | 3 candidates; closest (Q56816969) is 4 years from the window, likely an older namesake    |                        |
| T17        | My Life With the Walter Boys          | TV         |           4 | BR,DE,FR,IT       | Q113570499 | unique match                                                                              | DE,FR,BR,IT            |
| T18        | Salish & Jordan Matter                | TV         |           4 | BR,DE,FR,IT       |            | no Wikidata item with this exact English label                                            |                        |
| T19        | Blood Sacrifice                       | TV         |           4 | BR,DE,FR,IT       | Q136404689 | unique match                                                                              |                        |
| T20        | Outer Banks                           | TV         |           4 | BR,DE,FR,IT       | Q89414035  | unique match                                                                              | DE,FR,JP,BR,IT,KR      |

## Dropped pairs by reason

| reason                                      |   pairs |
|:--------------------------------------------|--------:|
| no dewiki sitelink                          |       7 |
| no frwiki sitelink                          |       2 |
| no itwiki sitelink                          |       6 |
| no jawiki sitelink                          |      12 |
| no kowiki sitelink                          |       9 |
| no ptwiki sitelink                          |       9 |
| title unmatched on Wikidata (all 6 markets) |      30 |

## Selected titles charting per market-week (all selected titles)

F = Films, TV = TV. Week = Sunday ending the Netflix week.

| week       |   DE F |   DE TV |   FR F |   FR TV |   JP F |   JP TV |   BR F |   BR TV |   IT F |   IT TV |   KR F |   KR TV |
|:-----------|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|
| 2026-07-05 |      1 |       3 |      1 |       3 |      1 |       1 |      1 |       3 |      1 |       3 |      1 |       2 |
| 2026-07-12 |      1 |       3 |      1 |       3 |      1 |       1 |      1 |       2 |      1 |       3 |      1 |       1 |
| 2026-07-19 |      3 |       3 |      3 |       3 |      1 |       1 |      1 |       2 |      3 |       2 |      1 |       1 |
| 2026-07-26 |      4 |       2 |      4 |       4 |      0 |       1 |      4 |       3 |      4 |       3 |      3 |       2 |
| 2026-08-02 |      4 |       2 |      4 |       3 |      3 |       1 |      4 |       2 |      4 |       2 |      2 |       1 |
| 2026-08-09 |      3 |       3 |      3 |       4 |      1 |       0 |      4 |       2 |      3 |       3 |      1 |       2 |
| 2026-08-16 |      2 |       2 |      3 |       4 |      1 |       1 |      3 |       2 |      3 |       3 |      1 |       2 |
| 2026-08-23 |      3 |       4 |      2 |       5 |      2 |       1 |      2 |       4 |      3 |       4 |      2 |       1 |
| 2026-08-30 |      6 |       5 |      5 |       5 |      4 |       0 |      5 |       4 |      5 |       5 |      4 |       1 |
| 2026-09-06 |      5 |       4 |      5 |       4 |      2 |       0 |      4 |       2 |      6 |       4 |      3 |       1 |
| 2026-09-13 |      2 |       3 |      2 |       2 |      1 |       0 |      2 |       0 |      2 |       2 |      2 |       0 |
| 2026-09-20 |      2 |       2 |      2 |       0 |      0 |       0 |      2 |       0 |      2 |       0 |      0 |       0 |

## Same, restricted to pairs with a Wikipedia article in that market

| week       |   DE F |   DE TV |   FR F |   FR TV |   JP F |   JP TV |   BR F |   BR TV |   IT F |   IT TV |   KR F |   KR TV |
|:-----------|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|-------:|--------:|
| 2026-07-05 |      0 |       2 |      1 |       2 |      1 |       0 |      0 |       0 |      1 |       1 |      1 |       1 |
| 2026-07-12 |      0 |       2 |      1 |       2 |      1 |       0 |      0 |       0 |      1 |       1 |      1 |       1 |
| 2026-07-19 |      0 |       2 |      1 |       2 |      0 |       0 |      0 |       0 |      1 |       1 |      0 |       1 |
| 2026-07-26 |      0 |       1 |      2 |       3 |      0 |       0 |      1 |       0 |      1 |       1 |      0 |       1 |
| 2026-08-02 |      0 |       1 |      2 |       3 |      0 |       0 |      1 |       0 |      1 |       0 |      0 |       1 |
| 2026-08-09 |      1 |       2 |      3 |       4 |      0 |       0 |      2 |       1 |      2 |       1 |      0 |       2 |
| 2026-08-16 |      1 |       2 |      3 |       4 |      0 |       0 |      2 |       1 |      2 |       2 |      0 |       2 |
| 2026-08-23 |      1 |       3 |      1 |       4 |      0 |       0 |      1 |       2 |      2 |       2 |      0 |       1 |
| 2026-08-30 |      2 |       3 |      3 |       3 |      0 |       0 |      2 |       1 |      2 |       2 |      1 |       1 |
| 2026-09-06 |      2 |       2 |      3 |       2 |      1 |       0 |      2 |       1 |      3 |       2 |      1 |       1 |
| 2026-09-13 |      1 |       1 |      2 |       1 |      0 |       0 |      1 |       0 |      1 |       1 |      1 |       0 |
| 2026-09-20 |      1 |       1 |      2 |       0 |      0 |       0 |      1 |       0 |      1 |       0 |      0 |       0 |
