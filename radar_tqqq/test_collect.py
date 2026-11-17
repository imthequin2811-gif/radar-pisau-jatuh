import datetime as dt
import unittest
from collect import coverage_time, parse_ndth, quote_yahoo, validate_row, UTC

class DataSafetyTests(unittest.TestCase):
    def test_missing_monday_prevents_false_tuesday_close(self):
        now = dt.datetime(2026, 11, 17, 1, tzinfo=UTC)
        self.assertEqual(coverage_time('2026-11-13', now), '2026-11-16T00:00:00+00:00')
        self.assertEqual(coverage_time('2026-11-16', now), '2026-11-17T00:00:00+00:00')

    def test_weekend_can_finish_closed_calendar_bucket(self):
        now = dt.datetime(2026, 11, 15, 8, tzinfo=UTC)
        self.assertEqual(coverage_time('2026-11-13', now), '2026-11-15T08:00:00+00:00')

    def test_future_and_invalid_quotes_rejected(self):
        now = dt.datetime(2026, 11, 17, tzinfo=UTC)
        with self.assertRaises(ValueError):
            quote_yahoo({'meta': {'symbol': '^VIX', 'regularMarketPrice': 25, 'regularMarketTime': now.timestamp()+600}}, now)
        with self.assertRaises(ValueError):
            validate_row({'date':'2026-11-16','open':20,'high':21,'low':19,'close':22})

    def test_quote_does_not_claim_verified_realtime(self):
        now = dt.datetime(2026, 11, 17, tzinfo=UTC)
        q = quote_yahoo({'meta':{'symbol':'DX-Y.NYB','regularMarketPrice':103.5,'regularMarketTime':now.timestamp()-30}}, now)
        self.assertFalse(q['liveVerified'])
        self.assertIsNone(q['delaySeconds'])
        self.assertEqual(q['asOf'],'2026-11-16T23:59:30+00:00')

    def test_ndth_current_session_is_not_automatically_final(self):
        page='Nasdaq 100 Stocks Above 200-Day Average<table><tr><td>16 Nov 26</td><td>52</td><td>55</td><td>48</td><td>49.5</td></tr><tr><td>13 Nov 26</td><td>54</td><td>56</td><td>52</td><td>55</td></tr></table>'
        during=dt.datetime(2026,11,16,19,tzinfo=UTC)
        after=dt.datetime(2026,11,17,1,tzinfo=UTC)
        self.assertEqual(parse_ndth(page,during)[-1]['date'],'2026-11-13')
        self.assertEqual(parse_ndth(page,after)[-1]['date'],'2026-11-16')

if __name__=='__main__':unittest.main()
