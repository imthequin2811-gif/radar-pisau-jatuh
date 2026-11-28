# LAB15 C002E — Free data only
No paid APIs, trading, or secrets. Existing radar_tqqq workflow owns the actual NDTH archive. New workflow audits data coverage daily at 00:00 UTC (07:00 WIB, schedule may be delayed) and supports Run workflow. It commits only status metadata, never raw Yahoo/FRED downloads or strategy settings. GitHub's working directory for supplemental raw data is temporary; durable supplemental history lives in a local folder. No changes to LAB14 or existing workflows. Run locally:
    python -m pip install -r research/lab15/requirements.txt
    python research/lab15/collect_free.py --self-test
    python research/lab15/collect_free.py
Optional research (longer; free feed may lack delisted symbols):
    python research/lab15/collect_free.py --reconstruct
Actual NDTH is preferred over proxies. Reconstruction uses dated membership snapshots and full rolling price coverage, never today's members across old dates; still requires independent effective-date and ticker-identity audit. No extrapolation beyond last membership change in supplied archive. FRED is close-only, not OHLC. Do not publish raw vendor files unless allowed by provider. No synthetic holiday candles, no simulated trading. Crypto anchor C002C and all donor settings untouched. Coverage OK is not a strategy PASS.
