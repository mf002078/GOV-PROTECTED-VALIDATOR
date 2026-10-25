"""Conservative execution UTC: fixed TLS endpoint cross-checked with host clock.

No clock fallback, candidate-controlled URL, caller-provided CLI time or future
acceptance grace. This is not a signed timestamp or a Protected Validator.
"""
import datetime as dt
import email.utils
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

MAX_RESPONSE_SECONDS = 10
MAX_CLOCK_SKEW_SECONDS = 60


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("BLOCKED/NOT_VERIFIED: UTC endpoint redirect")


def acquire_utc():
    before = dt.datetime.now(dt.timezone.utc)
    started = time.monotonic()
    request = urllib.request.Request(
        'https://github.com/?utc_reference=' + uuid.uuid4().hex,
        headers={'Cache-Control': 'no-cache', 'Accept': 'text/html'})
    try:
        # Default HTTPS handler preserves certificate and hostname verification.
        with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
            values = response.headers.get_all('Date') or []
            if len(values) != 1:
                raise ValueError('missing or ambiguous HTTP Date')
            remote = email.utils.parsedate_to_datetime(values[0])
            if remote.tzinfo is None or remote.utcoffset() != dt.timedelta(0):
                raise ValueError('invalid UTC Date')
        elapsed = time.monotonic() - started
        after = dt.datetime.now(dt.timezone.utc)
        if elapsed > MAX_RESPONSE_SECONDS or elapsed < 0 or after < before:
            raise ValueError('unreliable clock or response latency')
        if abs((after - remote).total_seconds()) > MAX_CLOCK_SKEW_SECONDS:
            raise ValueError('UTC source stale or inconsistent with executor clock')
        # Freshness/skew limits never extend the acceptance deadline. Use the
        # earlier source and ZERO future tolerance; stale clocks only reject more.
        return min(remote, before)
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        raise ValueError('BLOCKED/NOT_VERIFIED: execution UTC unavailable: '
                         + type(exc).__name__) from None
