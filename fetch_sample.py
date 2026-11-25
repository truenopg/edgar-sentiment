"""Pull the last few 8-Ks for a watchlist and stash them as text.

Also writes data/filings.csv with the metadata (date, items) so later
steps can join scores to dates without hitting EDGAR again.
"""
import csv
from pathlib import Path

from edgar.client import recent_filings, filing_text

WATCHLIST = ["AAPL", "MSFT", "JPM", "XOM", "NVDA",
             "TSLA", "AMZN", "META", "JNJ", "BA"]

if __name__ == "__main__":
    rows = []
    for t in WATCHLIST:
        filings = recent_filings(t, form="8-K", limit=5)
        for f in filings:
            text = filing_text(f)
            rows.append({"ticker": f["ticker"], "accession": f["accession"],
                         "date": f["date"], "items": f["items"]})
            print(f"{f['ticker']:5s} {f['date']}  items={f['items'][:40]:40s} {len(text):7d} chars")
    out = Path("data/filings.csv")
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["ticker", "accession", "date", "items"])
        w.writeheader()
        w.writerows(rows)
    print("->", out)
