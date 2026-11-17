"""Backfill actual INDEX:NDTH via TradingView's anonymous public chart feed.

Optional dependency: websockets>=15,<16. No login or paid token is used.
The regular collector remains dependency-free and appends EODData observations.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import secrets
import time

from collect import DEST, NY, UTC, coverage_time, iso, validate_row

SYMBOL = 'INDEX:NDTH'
SOURCE = 'https://www.tradingview.com/symbols/INDEX-NDTH/'
FEED = 'wss://data.tradingview.com/socket.io/websocket?from=symbols%2FINDEX-NDTH%2F&type=chart'


def encode(method, params):
    payload = json.dumps({'m': method, 'p': params}, separators=(',', ':'))
    return '~m~' + str(len(payload)) + '~m~' + payload


def frames(message):
    position = 0
    while message.startswith('~m~', position):
        end = message.index('~m~', position + 3)
        length = int(message[position + 3:end])
        position = end + 3
        yield message[position:position + length]
        position += length


def fetch():
    from websockets.sync.client import connect
    session = 'cs_' + secrets.token_hex(6)
    bars, metadata = {}, None
    deadline = time.monotonic() + 45
    with connect(FEED, origin='https://www.tradingview.com', open_timeout=15, max_size=8_000_000) as ws:
        commands = [
            ('set_auth_token', ['unauthorized_user_token']),
            ('chart_create_session', [session, '']),
            ('resolve_symbol', [session, 'symbol_1', '=' + json.dumps({'symbol': SYMBOL, 'adjustment': 'splits'})]),
            ('create_series', [session, 'series_1', 's1', 'symbol_1', '1D', 10000]),
        ]
        for method, params in commands:
            ws.send(encode(method, params))
        done = False
        while not done:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('NDTH chart request did not finish; old archive untouched')
            for frame in frames(ws.recv(timeout=remaining)):
                if frame.startswith('~h~'):
                    ws.send('~m~' + str(len(frame)) + '~m~' + frame)
                    continue
                try:
                    packet = json.loads(frame)
                except ValueError:
                    continue
                method, params = packet.get('m'), packet.get('p', [])
                if method == 'symbol_resolved':
                    metadata = params[-1]
                elif method in ('timescale_update', 'du'):
                    for bar in params[1].get('series_1', {}).get('s', []):
                        values = bar['v']
                        bars[int(values[0])] = values
                elif method == 'series_completed':
                    done = True
                elif method in ('symbol_error', 'series_error', 'critical_error', 'protocol_error'):
                    raise ValueError('Provider rejected the public chart request: ' + method)
    rows = [{'date': dt.datetime.fromtimestamp(stamp, UTC).date().isoformat(),
             **dict(zip(('open', 'high', 'low', 'close'), values[1:5]))}
            for stamp, values in sorted(bars.items())]
    return {'symbol': SYMBOL, 'metadata': metadata, 'rows': rows, 'retrievedAt': iso(dt.datetime.now(UTC))}


def validate(payload, existing, now):
    metadata = payload.get('metadata') or {}
    if metadata.get('full_name') != SYMBOL or metadata.get('description') != 'Nasdaq 100 Stocks Above 200-Day Average':
        raise ValueError('Unexpected symbol identity')
    local = now.astimezone(NY)
    rows = [validate_row(r, breadth=True) for r in payload['rows']
            if r['date'] < local.date().isoformat() or (r['date'] == local.date().isoformat() and local.hour >= 18)]
    if len(rows) < 1000:
        raise ValueError('History is too short for this backfill; prior archive untouched')
    by_date = {r['date']: r for r in rows}
    if len(by_date) != len(rows):
        raise ValueError('Duplicate dates in chart history')
    overlap = []
    # Compare against recent independently collected EOD observations.
    for row in existing[-11:]:
        other = by_date.get(row['date'])
        if other:
            delta = max(abs(row[k] - other[k]) for k in ('open', 'high', 'low', 'close'))
            if delta > .02:
                raise ValueError('EOD cross-check disagrees on ' + row['date'])
            overlap.append({'date': row['date'], 'maxOHLCdifference': round(delta, 6)})
    if len(overlap) < 5:
        raise ValueError('Need at least five overlapping EOD observations before backfill')
    ordered = sorted(rows, key=lambda r: r['date'])
    gaps = [(a['date'], b['date']) for a, b in zip(ordered, ordered[1:])
            if (dt.date.fromisoformat(b['date']) - dt.date.fromisoformat(a['date'])).days > 7]
    if gaps:
        raise ValueError('Unexplained history gap longer than seven days: ' + str(gaps[:3]))
    return ordered, overlap


def backfill(path, payload):
    now = dt.datetime.now(UTC)
    data = json.loads(path.read_text())
    asset = data['assets']['NDTH']
    rows, overlap = validate(payload, asset['rows'], now)
    merged = {r['date']: r for r in rows}
    # Keep newer EOD observations and previously recorded final closes on overlap.
    merged.update({r['date']: r for r in asset['rows']})
    complete = sorted(merged.values(), key=lambda r: r['date'])
    archive = {'symbol': SYMBOL, 'source': 'TradingView public daily chart', 'sourceUrl': SOURCE,
               'firstDate': rows[0]['date'], 'lastDate': rows[-1]['date'], 'rows': len(rows),
               'retrievedAt': payload['retrievedAt'], 'validatedAt': iso(now),
               'eoddataOverlap': overlap, 'isProxy': False,
               'sha256Rows': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()}
    asset.update(rows=complete, firstDate=complete[0]['date'], lastDate=complete[-1]['date'],
                 status='ready', source='TradingView INDEX:NDTH + EODData', sourceUrl=SOURCE,
                 adjustment='Seri NDTH aktual; bukan rekonstruksi konstituen dan bukan NDX.', isProxy=False,
                 reason='Histori NDTH sejak 2006; pembaruan EOD harian diteruskan dari EODData.',
                 historyArchive=archive, continuationSourceUrl='https://eoddata.com/stockquote/INDEX/NDTH.htm',
                 retrievedAt=iso(now), historyFetchedAt=iso(now), historyFetchStatus='OK',
                 dataThroughAt=coverage_time(complete[-1]['date'], now))
    asset.pop('historyError', None)
    asset['latestQuote'] = {'price': complete[-1]['close'], 'asOf': None, 'sessionDate': complete[-1]['date'],
                            'mode': 'EOD', 'source': 'EODData · INDEX:NDTH', 'liveVerified': False}
    data.update(generatedAt=iso(now), asOf=iso(now))
    temp = path.with_suffix('.backfill.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    temp.replace(path)
    print(json.dumps({k: archive[k] for k in ['symbol', 'rows', 'firstDate', 'lastDate']}))
    print('Cross-check:', len(overlap), 'recent EOD rows agree within 0.02 points')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=Path, default=DEST)
    parser.add_argument('--payload', type=Path, help='Use a previously downloaded raw chart payload')
    args = parser.parse_args()
    payload = json.loads(args.payload.read_text()) if args.payload else fetch()
    backfill(args.path, payload)
