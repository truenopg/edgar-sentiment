"""Pull the last few 8-Ks for a small watchlist and stash them as text."""
from edgar.client import recent_filings, filing_text

WATCHLIST = ["AAPL", "MSFT", "JPM", "XOM", "NVDA"]

if __name__ == "__main__":
    for t in WATCHLIST:
        filings = recent_filings(t, form="8-K", limit=5)
        for f in filings:
            text = filing_text(f)
            print(f"{f['ticker']:5s} {f['date']}  items={f['items'][:40]:40s} {len(text):7d} chars")
