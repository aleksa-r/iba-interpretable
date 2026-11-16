"""The one download of the confirmation series (SPEC-2026-11-14-confirmation, section 1). Refuses unless the
spec is frozen and committed and the target panel does not exist yet.

  .venv/bin/python scripts/download_confirmation.py
Yahoo adjusted closes of the 21 series, one dated and hashed file under data/raw/, then the weekly target panel
(returns, realised variance, daily log returns) on the index of the factor panel, under
data/panels/weekly_confirmation/. A raw download that already exists is used, never repeated. Before the panel is
built every series is checked for coverage of the factor panel's period; a series that fails stops the script with
nothing built. Prints file names, row counts, dates and hashes; no return is printed or evaluated."""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from datetime import datetime, timezone

MAX_GAP_DAYS = 10            # longest admissible distance between two consecutive prices of a series


def coverage_problems(raw, tickers, first, last):
    """Series whose prices do not cover [first - 7 days, last], or with a gap longer than MAX_GAP_DAYS (dates only, no values)."""
    import pandas as pd
    bad = {}
    for t in tickers:
        d = pd.DatetimeIndex(sorted(raw.loc[raw.symbol == t, "date"]))
        if len(d) == 0:
            bad[t] = "no rows"
        elif d[0] > first - pd.Timedelta(days=7):
            bad[t] = f"starts {d[0].date()}"
        elif d[-1] < last:
            bad[t] = f"ends {d[-1].date()}"
        else:
            inside = d[(d >= first - pd.Timedelta(days=7)) & (d <= last)]
            gap = int(pd.Series(inside).diff().dt.days.max())
            if gap > MAX_GAP_DAYS:
                bad[t] = f"gap of {gap} days"
    return bad


if __name__ == "__main__":
    import pandas as pd
    from iba.data.download import fetch_yahoo_daily
    from iba.data.panel import CONFIRMATION_TARGETS, build_weekly_targets
    from iba.data.universe import REPO
    from iba.protocol.spec import require_frozen
    from iba.protocol.study import CONFIRM, CONFIRM_DOWNLOAD, confirmation_series
    require_frozen(CONFIRM)
    out = os.path.join(REPO, "data", "panels", CONFIRMATION_TARGETS)
    if os.path.exists(os.path.join(out, "manifest.json")):
        sys.exit(f"{os.path.relpath(out, REPO)} exists: the confirmation series are downloaded once")
    tickers = confirmation_series()
    earlier = sorted(glob.glob(os.path.join(REPO, "data", "manifests", "yahoo_daily_conf_*.json")))
    if earlier:                                                    # a download was made and the panel was not built: use it, do not download again
        raw_path = os.path.join(REPO, json.load(open(earlier[0]))["file"])
        print(f"using the existing download {os.path.relpath(raw_path, REPO)}")
    else:
        tag = "conf_" + datetime.now(timezone.utc).strftime("%Y-%m-%d")
        raw_path = fetch_yahoo_daily(tickers, CONFIRM_DOWNLOAD["start"], CONFIRM_DOWNLOAD["end"], tag, confirmation_run=CONFIRM)
        print(f"downloaded {len(tickers)} series -> {os.path.relpath(raw_path, REPO)}")
    fdir = os.path.join(REPO, "data", "panels", "weekly_2026-11-11")
    idx = pd.read_csv(os.path.join(fdir, "factors.csv"), index_col=0, parse_dates=True).index
    bad = coverage_problems(pd.read_csv(raw_path, parse_dates=["date"]), tickers, idx.min(), idx.max())
    if bad:
        sys.exit(f"coverage problems, panel NOT built (record a deviation before anything else): {bad}")
    sha = build_weekly_targets(raw_path, fdir, out, confirmation_run=CONFIRM)
    man = json.load(open(os.path.join(out, "manifest.json")))
    print(f"weekly panel: {man['weeks']} weeks, {man['first']} to {man['last']}, {len(man['series'])} series; hashes {json.dumps(sha)}")
