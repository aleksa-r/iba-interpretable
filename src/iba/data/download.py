"""Daily adjusted closes from Yahoo for DEVELOPMENT series (or, with a frozen spec id, confirmation
series). Every ticker passes the confirmation guard before a request is made. One dated file per
download, long format (date, symbol, adj_close), with its sha256 written to data/manifests/."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd

from .universe import REPO, guard


def fetch_yahoo_daily(tickers: List[str], start: str, end: Optional[str], tag: str,
                      confirmation_run: Optional[str] = None) -> str:
    import yfinance as yf
    g = guard(confirmation_run)
    for t in tickers:
        g.check(t)
    rows = []
    for t in tickers:
        df = yf.download(t, start=start, end=end, auto_adjust=False, progress=False, threads=False)
        if df is None or df.empty:
            raise RuntimeError(f"no data for {t}")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        s = df["Adj Close"].dropna()
        rows.append(pd.DataFrame({"date": s.index.strftime("%Y-%m-%d"), "symbol": t, "adj_close": s.values}))
    out = pd.concat(rows, ignore_index=True)
    os.makedirs(os.path.join(REPO, "data", "raw"), exist_ok=True)
    path = os.path.join(REPO, "data", "raw", f"yahoo_daily_{tag}.csv")
    out.to_csv(path, index=False, float_format="%.6f")
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    man = {"file": os.path.relpath(path, REPO), "sha256": sha, "tickers": tickers, "start": start, "end": end,
           "rows": int(len(out)), "first": out.date.min(), "last": out.date.max(),
           "downloaded": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": "Yahoo Finance (yfinance), Adj Close",
           "confirmation_run": confirmation_run}
    with open(os.path.join(REPO, "data", "manifests", f"yahoo_daily_{tag}.json"), "w") as fh:
        json.dump(man, fh, indent=2)
    return path
