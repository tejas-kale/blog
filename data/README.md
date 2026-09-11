# US data-scientist employment dataset

Run the builder from the repository root:

```sh
uv run --with duckdb scripts/build_data_scientist_dataset.py
```

It discovers the latest available official CPS basic monthly files at run time,
downloads compressed files to `/tmp/cps-basic-cache`, and writes
`data/data_scientists.duckdb`. Raw survey files are not committed. The public-use
zips contain fixed-width `.dat` records (Census also publishes uncompressed
`.csv` files separately); the builder reads the `.dat` layout.

The primary occupation is Census 2018 code `1240`. This is the official Census
code that contains “Data scientists (15-2051)”, but it also contains other
mathematical-science occupations. The result must therefore be described as a
combined CPS category, not as a clean standalone count of data scientists.

After a builder run, derived tables are also written as CSV:

- `cps_1240_monthly.csv` — monthly CPS 1240 employment (rounded)
- `oews_15-2051_annual.csv` — May OEWS 15-2051 comparison points
- `monthly_cps.csv`, `annual_oews.csv`, `methodology.csv` — full DuckDB dumps
