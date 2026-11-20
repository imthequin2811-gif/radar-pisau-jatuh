#!/usr/bin/env python3
"""Refresh standalone Radar Bond 02A Treasury data without touching other LOCKs.
Primary: US Treasury CSV, then official XML. Secondary: GitHub Treasury mirror.
Cache is retained if all sources fail; missing data are never invented.
"""
from __future__ import annotations
import csv
import datetime as dt
import io
import json
import os
from pathlib import Path
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "treasury_7tenor_latest.csv"
STATUS = ROOT / "data" / "treasury_7tenor_latest_status.json"
DASHBOARD = ROOT / "RADAR_BOND_02A_LATEST.html"
TEMPLATE = ROOT / "RADAR_BOND_02A_7TENOR_ABSOLUT_INERSIA24_2026-11-18.html"
TENORS = ["2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
MIRROR_URL = "https://raw.githubusercontent.com/fujiapple852/yield/master/data/us_treasury_yield_curve_history.csv"
OFFICIAL_BASE = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
HEADERS = {"User-Agent": "RadarBondResearch/1.0 (public Treasury daily par yield; GitHub Actions)", "Accept": "text/csv,application/xml,text/xml,*/*"}

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=24) as rsp:
        content = rsp.read(4_000_000)
    if len(content) < 50:
        raise ValueError("empty/too short response")
    return content

def normalize_date(value: str) -> str:
    s = (value or "").strip().split("T")[0]
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError("unrecognized date "+repr(value))

def decimal(v):
    try:
        x = float(str(v).strip())
        if 0 < x < 25:
            return x
    except (ValueError, TypeError):
        pass
    return None

def parse_csv(content: bytes) -> dict[str, dict[str, float | None]]:
    text = content.decode("utf-8-sig", "replace")
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    def canon(k):
        return re.sub(r"[^a-z0-9]", "", k.lower())
    h = {canon(k): k for k in headers}
    mapping = {
        "2Y": ["2y", "2yr", "2year", "bc2year"],
        "3Y": ["3y", "3yr", "3year", "bc3year"],
        "5Y": ["5y", "5yr", "5year", "bc5year"],
        "7Y": ["7y", "7yr", "7year", "bc7year"],
        "10Y": ["10y", "10yr", "10year", "bc10year"],
        "20Y": ["20y", "20yr", "20year", "bc20year"],
        "30Y": ["30y", "30yr", "30year", "bc30year"],
    }
    dates = h.get("date") or h.get("newdate")
    cols = {t: next((h[x] for x in cand if x in h), None) for t, cand in mapping.items()}
    if not dates or not all(cols.values()):
        raise ValueError("not a complete seven-tenor Treasury CSV: " + repr(headers[:20]))
    out = {}
    for row in reader:
        try:
            day = normalize_date(row.get(dates, ""))
        except (ValueError, TypeError):
            continue
        if day > (dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1)).isoformat():
            continue
        vals = {t: decimal(row.get(col)) for t, col in cols.items()}
        if sum(v is not None for v in vals.values()) >= 5:
            out[day] = vals
    if not out:
        raise ValueError("no valid data from CSV")
    return out

def parse_xml(content: bytes) -> dict[str, dict[str, float | None]]:
    root = ET.fromstring(content)
    out = {}
    for e in root.iter():
        if e.tag.rsplit("}", 1)[-1].lower() != "entry":
            continue
        fields = {}
        for node in e.iter():
            leaf = node.tag.rsplit("}", 1)[-1].upper()
            if leaf in {"NEW_DATE", "BC_2YEAR", "BC_3YEAR", "BC_5YEAR", "BC_7YEAR",
                        "BC_10YEAR", "BC_20YEAR", "BC_30YEAR"}:
                fields[leaf] = (node.text or "").strip()
        if not fields.get("NEW_DATE"):
            continue
        try:
            day = normalize_date(fields["NEW_DATE"])
        except ValueError:
            continue
        vals = {t: decimal(fields.get("BC_"+t[:-1]+"YEAR")) for t in TENORS}
        if sum(v is not None for v in vals.values()) >= 5:
            out[day] = vals
    if not out:
        raise ValueError("no usable entries in Treasury XML")
    return out

def read_local():
    if DATA.exists() and DATA.stat().st_size:
        return parse_csv(DATA.read_bytes())
    return {}

def write_csv(table):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with io.StringIO() as buff:
        writer = csv.writer(buff, lineterminator="\n")
        writer.writerow(["date", *TENORS])
        for d in sorted(table):
            vals = table[d]
            writer.writerow([d, *[f"{vals[t]:.2f}" if vals.get(t) is not None else "" for t in TENORS]])
        content = buff.getvalue()
    if not DATA.exists() or DATA.read_text() != content:
        DATA.write_text(content, encoding="utf-8")

def business_days_after(day: str, today: dt.date) -> int:
    d = dt.date.fromisoformat(day)
    count = 0
    while d < today:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            count += 1
    return max(0,count)

def refresh_dashboard():
    if not TEMPLATE.exists():
        return False
    h = TEMPLATE.read_text(encoding="utf-8")
    csvtext = DATA.read_text(encoding="utf-8").strip()
    h, num = re.subn(r'(<script id="treasury-raw" type="text/plain">).*?(</script>)',
                     lambda m: m.group(1) + csvtext + m.group(2), h, count=1, flags=re.S)
    if num != 1:
        raise ValueError("cannot find embedded Treasury data in reference dashboard")
    h = h.replace("const now='2026-11-18'; // as-of snapshot; do not silently pretend refreshed",
                  "const now=new Date().toISOString().slice(0,10); // UTC clock; source freshness displayed separately")
    h = h.replace("const last='2026-11-18',cut=period==='4m'?'2026-07-18':'2025-11-18';",
                  "const last=now, c=new Date(now+'T00:00:00Z'); c.setUTCMonth(c.getUTCMonth()-(period==='4m'?4:12)); const cut=c.toISOString().slice(0,10);")
    h = h.replace("data dibekukan 18 November 2026", "data diperbarui oleh sumber GitHub terjadwal")
    h = h.replace("tidak dibandingkan baris-per-baris dengan CSV Treasury resmi 2026",
                  "data resmi yang tersedia diprioritaskan; audit metadata di treasury_7tenor_latest_status.json")
    if not DASHBOARD.exists() or DASHBOARD.read_text(encoding="utf-8") != h:
        DASHBOARD.write_text(h, encoding="utf-8")
        return True
    return False

def main():
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    merged = read_local()
    original_count = len(merged)
    sources = {}
    errors = {}
    new_dates = set()
    # Mirrors fill historical gaps; never overwrite locally recorded official data on equal dates.
    try:
        mirror = parse_csv(fetch(MIRROR_URL))
        for d, values in mirror.items():
            if d not in merged:
                merged[d] = values
                new_dates.add(d)
            elif d < "2026-01-01":  # historical corrections on the mirror are allowed
                merged[d] = values
        sources["github_mirror"] = max(mirror)
    except Exception as exc:
        errors["github_mirror"] = str(exc)[:350]
    # Primary current year: official CSV then official XML if CSV fails.
    # Do not treat XML as nonofficial; both endpoints come from US Treasury.
    for year in (today.year - 1, today.year):
        csvurl = (OFFICIAL_BASE + f"daily-treasury-rates.csv/{year}/all"
                  + f"?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv")
        xmlurl = (OFFICIAL_BASE + "pages/xml"
                  + f"?data=daily_treasury_yield_curve&field_tdr_date_value={year}")
        official = None
        for label, url, parser in (("treasury_csv", csvurl, parse_csv),
                                   ("treasury_xml", xmlurl, parse_xml)):
            try:
                official = parser(fetch(url))
                sources[label + "_" + str(year)] = max(official)
                break
            except Exception as exc:
                errors[label + "_" + str(year)] = str(exc)[:350]
        if official:
            for d, vals in official.items():
                # retain valid existing tenor if official record has missing fields
                previous = merged.get(d, {})
                merged[d] = {t: vals[t] if vals.get(t) is not None else previous.get(t) for t in TENORS}
                new_dates.add(d)
    if not merged:
        raise RuntimeError("No cached data, no official Treasury and no mirror. Refuse fabrication.")
    last = max(merged)
    age = business_days_after(last,today)
    stale = age > 3
    write_csv(merged)
    regenerated = refresh_dashboard()
    marker = "CURRENT" if not stale else "STALE_CHECK_DATA"
    status = {
        "data_type":"US_TREASURY_DAILY_PAR_YIELD_CURVE",
        "status":marker,
        "as_of_utc":now.isoformat(timespec="seconds"),
        "last_observation_us_session":last,
        "last_yields_pct":merged[last],
        "2s10s_basis_points": round((merged[last]["10Y"]-merged[last]["2Y"])*100,2) if merged[last].get("10Y") and merged[last].get("2Y") else None,
        "5s30s_basis_points": round((merged[last]["30Y"]-merged[last]["5Y"])*100,2) if merged[last].get("30Y") and merged[last].get("5Y") else None,
        "records":len(merged),
        "days_since_latest_weekdays_approx":age,
        "source_latest":sources,
        "source_errors":errors,
        "historical_source":MIRROR_URL,
        "primary_source":"U.S. Treasury official CSV/XML yearly endpoints",
        "policy":"Never forward fill holiday/zero yield or substitute 10Y from another methodology.",
        "dashboard_regenerated":regenerated,
        "changed_dates_this_run":len(new_dates),
        "original_cache_rows":original_count,
        "important":"Scheduled publication may lag or GitHub Actions may be disabled; verify workflow runs."
    }
    STATUS.write_text(json.dumps(status,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"latest":last,"status":marker,"records":len(merged),"sources":sources,"errors":errors},indent=2))
    if stale:
        print("WARNING: Treasury snapshot stale; do not claim live signals.", file=sys.stderr)
        sys.exit(1)

if __name__=="__main__":
    main()
