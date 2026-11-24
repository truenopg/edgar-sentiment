"""Thin SEC EDGAR client: ticker -> recent filings -> plain text.

EDGAR is public and free; it only asks for a declared User-Agent and
polite pacing (sec.gov/search-faq). We cache everything under data/ so a
second run never re-downloads.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

UA = {"User-Agent": "edgar-sentiment research pgadmcn@gmail.com"}
DATA = Path(__file__).resolve().parent.parent / "data"

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
_DOC = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"

_last_hit = 0.0


def _get(url: str) -> requests.Response:
    global _last_hit
    wait = 0.12 - (time.time() - _last_hit)  # stay well under 10 req/s
    if wait > 0:
        time.sleep(wait)
    r = requests.get(url, headers=UA, timeout=30)
    _last_hit = time.time()
    r.raise_for_status()
    return r


def ticker_to_cik(ticker: str) -> str:
    cache = DATA / "company_tickers.json"
    if cache.exists():
        table = json.loads(cache.read_text())
    else:
        DATA.mkdir(exist_ok=True)
        table = _get(_TICKERS_URL).json()
        cache.write_text(json.dumps(table))
    t = ticker.upper()
    for row in table.values():
        if row["ticker"].upper() == t:
            return str(row["cik_str"]).zfill(10)
    raise KeyError(f"ticker not in EDGAR table: {ticker}")


def recent_filings(ticker: str, form: str = "8-K", limit: int = 20) -> list[dict]:
    cik = ticker_to_cik(ticker)
    sub = _get(_SUBMISSIONS.format(cik=cik)).json()
    rec = sub["filings"]["recent"]
    out = []
    for i, f in enumerate(rec["form"]):
        if f != form:
            continue
        out.append({
            "ticker": ticker.upper(),
            "form": f,
            "date": rec["filingDate"][i],
            "accession": rec["accessionNumber"][i],
            "primary_doc": rec["primaryDocument"][i],
            "items": rec.get("items", [""] * len(rec["form"]))[i],
        })
        if len(out) >= limit:
            break
    return out


def html_to_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"&amp;", "&", text)
    return re.sub(r"\s+", " ", text).strip()


def filing_text(filing: dict) -> str:
    cik_int = int(ticker_to_cik(filing["ticker"]))
    acc_nodash = filing["accession"].replace("-", "")
    cache = DATA / f"{filing['ticker']}_{acc_nodash}.txt"
    if cache.exists():
        return cache.read_text()
    url = _DOC.format(cik_int=cik_int, acc_nodash=acc_nodash, doc=filing["primary_doc"])
    text = html_to_text(_get(url).text)
    cache.write_text(text)
    return text
