"""Synthetic HTTP metadata only: these tests never contact a time endpoint."""
import datetime as dt
import email.message
import unittest
from unittest.mock import patch

from validator import utc_reference as clock

NOW=dt.datetime(2026,10,25,2,tzinfo=dt.timezone.utc)


class ClockTests(unittest.TestCase):
    def acquire(self, date='Sun, 25 Oct 2026 01:59:55 GMT', delay=0.1, duplicate=False,
                local_before=NOW, local_after=NOW):
        headers=email.message.Message()
        if date is not None: headers['Date']=date
        if duplicate: headers['Date']=date
        with patch.object(clock.urllib.request,'build_opener') as builder, \
                patch.object(clock.dt,'datetime',wraps=dt.datetime) as dates, \
                patch.object(clock.time,'monotonic',side_effect=[1.0,1.0+delay]):
            dates.now.side_effect=[local_before,local_after]
            builder.return_value.open.return_value.__enter__.return_value.headers=headers
            return clock.acquire_utc()

    def test_verified_conservative_reference(self):
        self.assertEqual(NOW-dt.timedelta(seconds=5),self.acquire())

    def test_remote_ahead_clamped_to_host(self):
        self.assertEqual(NOW,self.acquire(date='Sun, 25 Oct 2026 02:00:02 GMT'))

    def test_missing_date_fails(self):
        with self.assertRaisesRegex(ValueError,'BLOCKED/NOT_VERIFIED'): self.acquire(date=None)

    def test_duplicate_date_fails(self):
        with self.assertRaises(ValueError): self.acquire(duplicate=True)

    def test_malformed_date_fails(self):
        with self.assertRaises(ValueError): self.acquire(date='not a timestamp')

    def test_stale_date_fails(self):
        with self.assertRaises(ValueError): self.acquire(date='Sun, 25 Oct 2026 01:58:59 GMT')

    def test_clock_disagreement_fails(self):
        with self.assertRaises(ValueError): self.acquire(date='Sun, 25 Oct 2026 02:01:01 GMT')

    def test_slow_response_fails(self):
        with self.assertRaises(ValueError): self.acquire(delay=11)

    def test_host_clock_rollback_fails(self):
        with self.assertRaises(ValueError): self.acquire(local_after=NOW-dt.timedelta(seconds=1))

    def test_network_failure_no_fallback(self):
        with patch.object(clock.urllib.request,'build_opener') as builder:
            builder.return_value.open.side_effect=OSError('synthetic denial')
            with self.assertRaisesRegex(ValueError,'BLOCKED/NOT_VERIFIED'): clock.acquire_utc()

    def test_tls_failure_no_fallback(self):
        with patch.object(clock.urllib.request,'build_opener') as builder:
            builder.return_value.open.side_effect=clock.urllib.error.URLError('synthetic TLS failure')
            with self.assertRaises(ValueError): clock.acquire_utc()

    def test_redirect_fails(self):
        with self.assertRaises(ValueError):
            clock.NoRedirect().redirect_request(None,None,302,'redirect',{},'https://synthetic.invalid')
