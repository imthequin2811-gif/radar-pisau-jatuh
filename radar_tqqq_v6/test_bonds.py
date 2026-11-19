import unittest, datetime as dt, tempfile, json
from pathlib import Path
from unittest.mock import patch
import collect_bonds as c
NOW=dt.datetime(2026,11,19,1,tzinfo=dt.timezone.utc)
def xml(date='2026-11-18',value='4.80',extra=''):
    return f'<feed xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"><m:properties><d:NEW_DATE>{date}T00:00:00</d:NEW_DATE><d:BC_2YEAR>{value}</d:BC_2YEAR><d:BC_3YEAR m:null="true"/></m:properties>{extra}</feed>'
class Tests(unittest.TestCase):
    def test_null_not_zero_and_actual_zero_allowed(self):
        self.assertEqual(c.parse(xml(value='0'),2026,NOW)[0][1:],[0,None,None,None,None,None,None])
    def test_reject_wrong_year_nonfinite_out_of_range(self):
        for value in ['nan','inf','-1','101']:
            with self.assertRaises(ValueError): c.parse(xml(value=value),2026,NOW)
        with self.assertRaises(ValueError): c.parse(xml(),2025,NOW)
    def test_future_and_unfinished_day_excluded(self):
        for date in ['2026-11-19','2027-01-01']:
            with self.assertRaises(ValueError): c.parse(xml(date=date),2026,NOW)
        with self.assertRaises(ValueError): c.parse(xml(),2026,NOW-dt.timedelta(hours=4))
    def test_duplicates_rejected(self):
        text=xml();inner=text[text.index('<m:properties>'):text.index('</m:properties>')+len('</m:properties>')]
        with self.assertRaises(ValueError):c.parse(xml(extra=inner),2026,NOW)
    def test_source_failure_preserves_archive_and_is_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bonds.json';row=['2026-11-17',4.8,4.9,5,5.1,5.2,5.3,5.4]
            p.write_text(json.dumps({'rows':[row],'lastDate':row[0],'officialYears':[2026]}))
            with patch.object(c,'fetch',side_effect=RuntimeError('provider offline')): data=c.collect(p)
            self.assertEqual(data['rows'],[row]);self.assertEqual(data['health'],'degraded');self.assertEqual(len(data['errors']),2)
if __name__=='__main__':unittest.main()
