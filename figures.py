"""Plot finbert filing tone over time, one panel per ticker."""
import csv
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path(__file__).parent / "data"
FIGS = Path(__file__).parent / "report" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

dates = {r["accession"].replace("-", ""): r["date"] for r in csv.DictReader((DATA / "filings.csv").open())}
scores = list(csv.DictReader((DATA / "scores.csv").open()))

by_ticker = {}
for r in scores:
    if r["accession"] in dates and r["sentiment"]:
        d = datetime.strptime(dates[r["accession"]], "%Y-%m-%d")
        by_ticker.setdefault(r["ticker"], []).append((d, float(r["sentiment"])))

tickers = sorted(by_ticker)
fig, axes = plt.subplots(2, 5, figsize=(16, 6), sharex=False, sharey=True)
fig.suptitle("finbert tone of recent 8-K filings (mean P(pos) - P(neg) over sentences)")
for ax, t in zip(axes.flat, tickers):
    pts = sorted(by_ticker[t])
    ax.axhline(0, color="black", lw=0.6)
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", ms=4, lw=1)
    ax.set_title(t, fontsize=10)
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.tick_params(axis="y", labelsize=7)
for ax in axes.flat[len(tickers):]:
    ax.axis("off")
fig.text(0.5, 0.01, "filing date", ha="center")
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
out = FIGS / "filing_tone.png"
fig.savefig(out, dpi=110)
print("->", out)
