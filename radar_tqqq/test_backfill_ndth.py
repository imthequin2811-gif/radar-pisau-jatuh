import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest

from backfill_ndth import SYMBOL, backfill, validate
from collect import UTC


class BackfillTests(unittest.TestCase):
    def setUp(self):
        first = dt.date(2022, 1, 3)
        rows = []
        day = first
        while len(rows) < 1000:
            if day.weekday() < 5:
                rows.append({'date': day.isoformat(), 'open': 50, 'high': 52, 'low': 49, 'close': 51})
            day += dt.timedelta(days=1)
        self.payload = {'symbol': SYMBOL, 'metadata': {'full_name': SYMBOL, 'description': 'Nasdaq 100 Stocks Above 200-Day Average'},
                        'rows': rows, 'retrievedAt': '2026-11-17T12:00:00+00:00'}
        self.existing = copy.deepcopy(rows[-11:])
        self.now = dt.datetime(2026, 11, 17, 15, tzinfo=UTC)

    def test_confirm_identity_overlap_and_reject_wrong_close(self):
        rows, overlap = validate(self.payload, self.existing, self.now)
        self.assertEqual(len(rows), 1000)
        self.assertEqual(len(overlap), 11)
        self.existing[-1]['close'] = 50
        with self.assertRaisesRegex(ValueError, 'cross-check disagrees'):
            validate(self.payload, self.existing, self.now)

    def test_reject_proxy_duplicate_and_out_of_range(self):
        for kind in ['proxy', 'duplicate', 'bounds']:
            payload = copy.deepcopy(self.payload)
            if kind == 'proxy':
                payload['metadata']['full_name'] = 'NASDAQ:NDX'
            elif kind == 'duplicate':
                payload['rows'].append(payload['rows'][0])
            else:
                payload['rows'][0]['high'] = 101
            with self.assertRaises(ValueError):
                validate(payload, self.existing, self.now)

    def test_running_day_excluded(self):
        payload = copy.deepcopy(self.payload)
        payload['rows'].append({'date': '2026-11-17', 'open': 50, 'high': 52, 'low': 49, 'close': 51})
        rows, _ = validate(payload, self.existing, self.now)
        self.assertEqual(len(rows), 1000)

    def test_failed_validation_leaves_disk_untouched(self):
        payload = copy.deepcopy(self.payload)
        payload['metadata']['full_name'] = 'NASDAQ:NDX'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'market-data.json'
            original = json.dumps({'assets': {'NDTH': {'rows': self.existing}}})
            path.write_text(original)
            with self.assertRaises(ValueError):
                backfill(path, payload)
            self.assertEqual(path.read_text(), original)

if __name__ == '__main__':
    unittest.main()
