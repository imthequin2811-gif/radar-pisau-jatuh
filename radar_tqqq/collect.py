"""Public-source radar collector. Quotes never replace CLOSED daily OHLC."""
import argparse
import concurrent.futures
import copy
import csv
import datetime as dt
import html
import io
import json
import math
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data/tqqq_radar/market-data.json'
UTC = dt.timezone.utc
NY = ZoneInfo('America/New_York')
SYMBOLS = {'TQQQ': 'TQQQ', 'VIX': '^VIX', 'DXY': 'DX-Y.NYB'}
VIX_URL = 'https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv'
NDTH_URL = 'https://eoddata.com/stockquote/INDEX/NDTH.htm'

def iso(t):
    return t.astimezone(UTC).isoformat(timespec='seconds')

def download(url):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Radar personal market research)', 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=25) as response:
                return response.read(8000000).decode('utf-8-sig')
        except Exception as exc:
            error = exc
            time.sleep(attempt + 1)
    raise RuntimeError(str(error))

def yahoo(symbol, interval, range_):
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(symbol, safe='')
    url += '?' + urllib.parse.urlencode({'range': range_, 'interval': interval, 'events': 'splits'})
    result = json.loads(download(url))['chart']['result']
    if not result:
        raise ValueError('Yahoo response has no result')
    if result[0]['meta']['symbol'] != symbol:
        raise ValueError('Unexpected symbol')
    return result[0]

def number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)

def coverage_time(last_date, now):
    """Never close a calendar candle across a weekday missing from the daily feed."""
    next_day = dt.date.fromisoformat(last_date) + dt.timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += dt.timedelta(days=1)
    # Weekend coverage is known; exchange holidays are conservatively not inferred.
    boundary = dt.datetime.combine(next_day, dt.time(), UTC)
    return iso(min(now, boundary))

def validate_row(r, breadth=False):
    dt.date.fromisoformat(r['date'])
    if not all(number(r.get(k)) and r[k] >= 0 for k in ('open', 'high', 'low', 'close')):
        raise ValueError('Invalid OHLC')
    if r['high'] + 1e-5 < max(r['open'], r['close'], r['low']) or r['low'] - 1e-5 > min(r['open'], r['close']):
        raise ValueError('Inconsistent OHLC')
    if breadth and any(r[k] > 100 for k in ('open', 'high', 'low', 'close')):
        raise ValueError('Breadth outside 0..100')
    return r

def daily_yahoo(j, now):
    meta = j['meta']
    tz = ZoneInfo(meta['exchangeTimezoneName'])
    local_today = now.astimezone(tz).date()
    period = meta.get('currentTradingPeriod', {}).get('regular', {})
    session_start = dt.datetime.fromtimestamp(period.get('start', 0), tz).date()
    session_end = period.get('end', float('inf'))
    quotes = j['indicators']['quote'][0]
    rows = []
    for i, stamp in enumerate(j.get('timestamp', [])):
        day = dt.datetime.fromtimestamp(stamp, tz).date()
        if day < dt.date(2020, 1, 1) or day > local_today:
            continue
        # A current-session daily bar is provisional until the provider's session end.
        if day == local_today and not (day == session_start and now.timestamp() >= session_end + 300):
            continue
        values = {k: quotes[k][i] for k in ('open', 'high', 'low', 'close')}
        if any(v is None for v in values.values()):
            continue  # Empty provider holiday rows are not interpolated.
        row = {'date': day.isoformat(), **{k: round(v, 6) for k, v in values.items()}}
        rows.append(validate_row(row))
    if len(rows) < 300:
        raise ValueError('Unexpectedly short Yahoo history; previous history retained')
    return sorted({r['date']: r for r in rows}.values(), key=lambda r: r['date'])

def quote_yahoo(j, now):
    m = j['meta']; price = m.get('regularMarketPrice'); stamp = m.get('regularMarketTime')
    if not number(price) or price < 0 or not number(stamp) or stamp > now.timestamp() + 60:
        raise ValueError('Invalid/future quote')
    period = m.get('currentTradingPeriod', {}).get('regular', {})
    session = 'OPEN' if period.get('start', 0) <= now.timestamp() < period.get('end', 0) else 'CLOSED'
    return {'price': price, 'asOf': iso(dt.datetime.fromtimestamp(stamp, UTC)), 'fetchedAt': iso(now),
            'source': 'Yahoo Finance · ' + m['symbol'], 'mode': 'TIMESTAMPED_QUOTE',
            'marketSession': session, 'delaySeconds': None, 'liveVerified': False,
            'note': 'Quote bertimestamp; latensi feed tidak dijamin. GitHub polling bukan streaming real-time.'}

def parse_vix(text, now):
    rows = []
    for source in csv.DictReader(io.StringIO(text)):
        day = dt.datetime.strptime(source['DATE'], '%m/%d/%Y').date()
        if not dt.date(2020, 1, 1) <= day <= now.astimezone(NY).date():
            continue
        # Official daily file is the publication of completed observations.
        rows.append(validate_row({'date': day.isoformat(), **{k.lower(): float(source[k]) for k in ['OPEN', 'HIGH', 'LOW', 'CLOSE']}}))
    if len(rows) < 300:
        raise ValueError('Official VIX daily history unexpectedly short')
    return sorted({r['date']: r for r in rows}.values(), key=lambda r: r['date'])

def parse_ndth(text, now):
    if 'Nasdaq 100 Stocks Above 200-Day Average' not in text:
        raise ValueError('NDTH source identity changed')
    local = now.astimezone(NY)
    rows = []
    for tr in re.findall(r'<tr\b.*?</tr>', text, re.S | re.I):
        cells = [html.unescape(re.sub('<[^>]+>', '', x)).strip() for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', tr, re.S | re.I)]
        if len(cells) < 5:
            continue
        try:
            day = dt.datetime.strptime(cells[0], '%d %b %y').date()
        except ValueError:
            continue
        if day > local.date() or (day == local.date() and local.hour < 18):
            continue  # Do not relabel an intraday page row as final EOD.
        row = {'date': day.isoformat(), **{k: float(cells[i+1].replace(',', '')) for i, k in enumerate(['open', 'high', 'low', 'close'])}}
        rows.append(validate_row(row, breadth=True))
    if not rows:
        raise ValueError('No completed NDTH daily observations found')
    return sorted({r['date']: r for r in rows}.values(), key=lambda r: r['date'])

def fetch_history(symbol, now):
    if symbol == 'NDTH':
        return parse_ndth(download(NDTH_URL), now)
    if symbol == 'VIX':
        return parse_vix(download(VIX_URL), now)
    return daily_yahoo(yahoo(SYMBOLS[symbol], '1d', '10y'), now)

def collect(path=DEST, force=False):
    now = dt.datetime.now(UTC)
    data = json.loads(path.read_text())
    assets = data['assets']
    jobs = {}
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for symbol, asset in assets.items():
            last = asset.get('historyFetchedAt')
            # Refresh daily history every six hours; quotes every workflow run.
            due = force or not last or (now - dt.datetime.fromisoformat(last)).total_seconds() >= 21600
            if due:
                jobs[pool.submit(fetch_history, symbol, now)] = (symbol, 'history')
            if symbol in SYMBOLS:
                jobs[pool.submit(lambda s=symbol: quote_yahoo(yahoo(SYMBOLS[s], '5m', '5d'), now))] = (symbol, 'quote')
        for future in concurrent.futures.as_completed(jobs):
            symbol, kind = jobs[future]; asset = assets[symbol]
            asset[kind + 'AttemptAt'] = iso(now)
            try:
                result = future.result()
                if kind == 'history':
                    previous_last = asset.get('lastDate', '')
                    if result[-1]['date'] < previous_last:
                        raise ValueError('Provider history regressed; retained previous dataset')
                    if symbol == 'NDTH':
                        # Incremental actual NDTH archive. Never substitute a reconstructed proxy.
                        merged = {r['date']: r for r in asset.get('rows', [])}
                        merged.update({r['date']: r for r in result}); result = sorted(merged.values(), key=lambda r: r['date'])
                    asset['rows'] = result
                    asset.update(firstDate=result[0]['date'], lastDate=result[-1]['date'], retrievedAt=iso(now), historyFetchedAt=iso(now))
                    asset['dataThroughAt'] = coverage_time(result[-1]['date'], now)
                    if symbol == 'NDTH':
                        asset.update(status='partial' if len(result) < 300 else 'ready', reason='Arsip NDTH aktual bertambah harian; indikator hanya dihitung jika candle warm-up cukup.')
                        asset['latestQuote'] = {'price': result[-1]['close'], 'asOf': None, 'sessionDate': result[-1]['date'], 'mode': 'EOD', 'source': asset['source'], 'liveVerified': False}
                else:
                    asset['latestQuote'] = result
                asset[kind + 'FetchStatus'] = 'OK'; asset.pop(kind + 'Error', None)
            except Exception as exc:
                asset[kind + 'FetchStatus'] = 'ERROR'; asset[kind + 'Error'] = str(exc)[:300]
                errors.append(symbol + '/' + kind + ': ' + str(exc))
                # Preserve timestamps and data on error; never make old data look freshly observed.
    data.update(schemaVersion=2, generatedAt=iso(now), asOf=iso(now), updateMode='github-polling',
                pollMinutes=15, health='degraded' if errors else 'ok', errors=errors,
                eodCutoff=max(a.get('lastDate', '') for a in assets.values()),
                notes=['GitHub Actions memeriksa tiap 15 menit secara best-effort; antrean dapat terlambat.',
                       'Quote VIX/DXY/TQQQ terpisah dari OHLC EOD dan tidak mengubah indikator CLOSED.',
                       'NDTH sumber EOD aktual, bukan live intraday; arsip tidak diisi dengan proksi.'])
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp'); temp.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))); temp.replace(path)
    for symbol, asset in assets.items():
        q = asset.get('latestQuote', {})
        print(symbol, 'EOD', asset.get('lastDate'), len(asset.get('rows', [])), 'quote', q.get('price'), q.get('asOf') or q.get('sessionDate'), asset.get('historyFetchStatus'), asset.get('quoteFetchStatus'))
    for error in errors:
        print('SOURCE ERROR:', error)
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--force-history', action='store_true'); args = parser.parse_args()
    collect(force=args.force_history)
