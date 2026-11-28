# Review of /status/ and the source pages, typed in cl-6.data's session

Given by the session user, 28 Nov 2026, about 2026-11-28T02:28:18Z (typed mid-turn; their words, condensed and in order, nothing added).

1. Drop "Code from Portuguese organisations on GitHub" (github-pt): no value from it.
2. Source page, first thing to see: a rendering of the data we hold, the amount of data collected, the number of files, and a scale of it. Maybe a badge on the right. Work with a designer.
3. Explain what is problematic on a source with a problem. Capture how often it is collected (the user remembered "every 4 hours") and what each failed request is ("12 requests, one failed: what is that failed?").
4. Show insights: the data we hold, where it is used. On the API address, give more on past data. Add Swagger (OpenAPI) so they can consume it.
5. "Last runs: request failed feels very constant. Why is it always one that failed? What changed between runs, like a diff?" Link every run to the data (GitHub commits).
6. No link back to the status page from a source page (they had to use the browser).
7. Events: what is wrong; show the log of the process; what is up with the collector; where the data comes from.
8. Always show where the information comes from. Example: a source like the Agenda LX (WordPress) site should link to a source page that first renders it, then points to the JSON file; source file on the sources section; provenance, where it is stored, how many copies exist, the API addresses, the delta.
9. Analysis: do we need to call some sources several times a day? How many times do we check?
10. Open-Meteo raw forecast link shows plain JSON. "What is the error?" Every raw JSON should have a visualisation, maybe embedded. Apply to all sources.
11. A view per run: a data analysis that shows and links what changed between runs, on the different files, within reason (not massive). A first meta-analysis, of everything or per section.

Status of each: see cell notes sent to cl-6.maestro the same day.
