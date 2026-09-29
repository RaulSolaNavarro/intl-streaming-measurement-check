# Project brief: intl-streaming-measurement-check

## Goal

Build a one-day portfolio project that reconciles a streaming platform's own reported rankings (first-party) against an independent attention signal (third-party) across six international markets, then explains where and why the two sources disagree.

This project supports my application for an Analytics Manager role in international third-party audience measurement. The posting emphasizes: reconciling first-party vs. third-party data, evaluating measurement methodologies across markets, BigQuery and SQL, data visualization, and automating recurring reports. Every design choice should make those skills visible.

## Data sources

- **First-party:** Netflix Top 10 by country, the weekly TSV published at top10.netflix.com. Confirm the current download URL before coding against it.
- **Third-party signal:** Daily Wikipedia pageviews from the Wikimedia REST API (`/metrics/pageviews/per-article/`). Send a descriptive User-Agent header with contact info, per Wikimedia policy. Use `user` agent type and `all-access`.
- **Title mapping:** Use the Wikidata API (sitelinks) to map each English title to its article in each language edition. Do not hand-type translated titles.

## Scope (hard limits)

- **Markets and language editions:** Germany (de), France (fr), Japan (ja), Brazil (pt), Italy (it), South Korea (ko).
- **Titles:** For each market, every title in that market's Top 10 (Films and TV) across the window. No title cap and no minimum number of markets. A title-market pair exists only where the title charted in that market. TV seasons roll up to the show.
- **Window:** The most recent 12 complete Netflix weeks.
- **Title mapping order:** If a Wikidata item has a Netflix ID (P1874) and its label or alias matches the Netflix title, accept it directly. Only when no candidate has a Netflix ID, fall back to exact English label plus a type allowlist, with dates used only to break ties.
- If a title does not map cleanly to a language edition, drop that title-market pair and log it. Do not spend time forcing matches.
- **Reporting:** Report the mapping rate per market (titles charted vs. titles with an article in that language) and n per market-week, split by Films and TV.

## Default metric definitions

Propose changes in plan mode if these don't hold up against the real data.

- Aggregate daily pageviews to Netflix's weekly periods.
- **Agreement:** Spearman rank correlation per market-week, comparing Netflix rank against pageview rank among the titles charting that week. For any market-week with n under 4 mapped titles, fall back to pooled within-market agreement (ranks computed within each week, pooled across weeks) and report n.
- **Discrepancy flag:** a title-market-week where the two ranks differ by 5 or more positions.
- **Timing:** days between a title's pageview peak and its first Netflix chart week, by market.

## Environment

- Windows 11, PowerShell. Give PowerShell syntax for any command I need to run myself.
- Python in a local virtual environment (`.venv`). Record dependencies in `requirements.txt`.
- BigQuery project ID: `intl-streaming-measurement`. Dataset: `streaming_measurement`, location US.
- Authentication uses Application Default Credentials, already configured through gcloud. Never create service account keys or write credentials into the repo.
- Quarto for the report, rendered to `docs/` and published through GitHub Pages from the `main` branch `/docs` folder.

## Repo structure

```
/scripts     Python pipeline scripts, numbered in run order (01_pull_netflix.py, ...)
/sql         BigQuery queries saved as .sql files, one per analysis step
/data/raw    Downloaded source files (small enough to commit)
/data/processed  Cleaned tables loaded to BigQuery
/report      Quarto source files
/docs        Rendered Quarto site (GitHub Pages output)
```

## Phases and checkpoints

Work in four phases. **Stop at the end of each phase**, summarize what you did and what you found, and wait for my approval before starting the next.

1. **Data pull:** Netflix file, title selection, Wikidata mapping, pageview pull. Report the final title list and any dropped pairs.
2. **BigQuery load and SQL:** Load processed tables, write the join and metric queries in `/sql`. Report row counts and a sample of results.
3. **Analysis:** Compute agreement, discrepancies, and timing by market. Report the 3 or 4 strongest findings in plain language.
4. **Report:** Build the Quarto site with static charts (Plotly), a methodology section, a limitations section, and a short section on how this would run as an automated weekly refresh. Update README.md with a summary and the site link.

## Rules

- Ask before every `git push`. Commit locally with clear messages at the end of each phase.
- Never commit credentials, `.env` files, or anything in `AppData`.
- The pipeline must run end to end from scripts. No manual downloads or copy-paste steps.
- Comment code thoroughly. Write for a reader who has never seen the project.
- Keep charts static in the report. BigQuery tables may not persist long term.

## Limitations to document honestly

- Neither source is audience measurement. Netflix publishes ranks by country, not viewing hours by country. Wikipedia pageviews measure attention, not viewing.
- Language editions do not equal countries (pt covers Brazil and Portugal, de covers Germany, Austria, and Switzerland).
- Local audiences may not look up domestic titles the way foreign audiences do.

## Writing style for all prose (README, report, commit messages)

- Never use em dashes. Use commas, periods, or parentheses.
- No corporate buzzwords.
- Direct, active-voice prose with short paragraphs.
- First person in the README and report ("I built", "I found").
