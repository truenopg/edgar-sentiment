"""Score cached filing texts with finbert, one row per filing in scores.csv.

Sentence level: finbert is trained on short financial text, so whole
documents go in as sentences and the filing score is the mean
P(positive) - P(negative) over its sentences.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from transformers import pipeline

DATA = Path(__file__).parent / "data"
MAX_SENTENCES = 200  # evenly sampled when a filing is longer

_pipe = None


def scorer():
    global _pipe
    if _pipe is None:
        _pipe = pipeline("text-classification", model="ProsusAI/finbert", top_k=None, truncation=True, max_length=512)
    return _pipe


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    keep = [s.strip() for s in parts if 25 <= len(s) <= 1500]
    if len(keep) > MAX_SENTENCES:
        step = len(keep) / MAX_SENTENCES
        keep = [keep[int(i * step)] for i in range(MAX_SENTENCES)]
    return keep


def score_text(text: str) -> dict:
    sents = sentences(text)
    if not sents:
        return {"n_sentences": 0, "sentiment": None, "pos": None, "neg": None}
    pos = neg = 0.0
    for i in range(0, len(sents), 32):
        for res in scorer()(sents[i:i + 32]):
            p = {r["label"]: r["score"] for r in res}
            pos += p.get("positive", 0.0)
            neg += p.get("negative", 0.0)
    n = len(sents)
    return {"n_sentences": n, "sentiment": round(pos / n - neg / n, 4),
            "pos": round(pos / n, 4), "neg": round(neg / n, 4)}


def main() -> None:
    out = DATA / "scores.csv"
    done = set()
    if out.exists():
        import csv as _csv
        for r in _csv.DictReader(out.open()):
            done.add(r["accession"])
    import csv
    fresh = out.exists()
    with out.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["ticker", "accession", "n_sentences", "sentiment", "pos", "neg"])
        if not fresh:
            w.writeheader()
        for path in sorted(DATA.glob("*_*.txt")):
            ticker, acc = path.stem.split("_", 1)
            if acc in done:
                continue
            s = score_text(path.read_text())
            w.writerow({"ticker": ticker, "accession": acc, **s})
            fh.flush()
            print(ticker, acc[:10], s, flush=True)
    print("->", out)


if __name__ == "__main__":
    main()
