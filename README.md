# edgar-sentiment

Pulls recent SEC filings (8-Ks) from EDGAR for a small watchlist and scores
their tone with a finance-tuned language model (finbert), then plots how the
tone of a company's filings evolves.

Research toy, not investment advice: filing tone is descriptive text
analysis, not a price signal.

## Layout

- `edgar/client.py` - polite EDGAR client (declared UA, cached downloads)
- `fetch_sample.py` - grab the last few 8-Ks per watchlist ticker
- `data/` - cached filing text (gitignored)

## Data

SEC EDGAR public APIs (no key): `company_tickers.json`, `data.sec.gov`
submissions, filing documents under `www.sec.gov/Archives`.
