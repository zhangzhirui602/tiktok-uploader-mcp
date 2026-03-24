"""
Tests for CLI batch scheduling helpers
"""

import datetime
import os
from argparse import Namespace

import pytest
import pytz
from freezegun import freeze_time

from tiktok_uploader.cli import (
    generate_schedule_times,
    parse_schedule,
    validate_batch_args,
)

FILENAME = "test_cli.mp4"
COPENHAGEN = "Europe/Copenhagen"


def setup_function() -> None:
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write("test")


def teardown_function() -> None:
    if os.path.exists(FILENAME):
        os.remove(FILENAME)


# ---------------------------------------------------------------------------
# generate_schedule_times
# ---------------------------------------------------------------------------


def test_generate_schedule_times_count() -> None:
    start = datetime.datetime(2026, 3, 20, 10, 0)
    times = generate_schedule_times(start, interval_minutes=1440, count=3)
    assert len(times) == 3


def test_generate_schedule_times_first_equals_start() -> None:
    start = datetime.datetime(2026, 3, 20, 10, 0)
    times = generate_schedule_times(start, interval_minutes=1440, count=3)
    assert times[0] == start


def test_generate_schedule_times_24h_interval() -> None:
    start = datetime.datetime(2026, 3, 20, 10, 0)
    times = generate_schedule_times(start, interval_minutes=1440, count=3)
    assert times[1] == datetime.datetime(2026, 3, 21, 10, 0)
    assert times[2] == datetime.datetime(2026, 3, 22, 10, 0)


def test_generate_schedule_times_single_video() -> None:
    start = datetime.datetime(2026, 3, 20, 10, 0)
    times = generate_schedule_times(start, interval_minutes=1440, count=1)
    assert times == [start]


def test_generate_schedule_times_zero_count() -> None:
    start = datetime.datetime(2026, 3, 20, 10, 0)
    times = generate_schedule_times(start, interval_minutes=1440, count=0)
    assert times == []


def test_generate_schedule_times_crosses_midnight() -> None:
    start = datetime.datetime(2026, 3, 20, 23, 0)
    times = generate_schedule_times(start, interval_minutes=120, count=2)
    assert times[1] == datetime.datetime(2026, 3, 21, 1, 0)


def test_generate_schedule_times_copenhagen_aware() -> None:
    """UTC-aware datetimes (from timezone conversion) work correctly."""
    tz = pytz.timezone(COPENHAGEN)
    # 2026-03-20 is before DST (CET = UTC+1)
    start_local = tz.localize(datetime.datetime(2026, 3, 20, 10, 0))
    start_utc = start_local.astimezone(pytz.UTC)
    times = generate_schedule_times(start_utc, interval_minutes=1440, count=2)
    # Next day, same local time: 2026-03-21 10:00 CET = 09:00 UTC
    expected_utc = tz.localize(datetime.datetime(2026, 3, 21, 10, 0)).astimezone(
        pytz.UTC
    )
    assert times[1] == expected_utc


# ---------------------------------------------------------------------------
# validate_batch_args – file existence
# ---------------------------------------------------------------------------


def test_validate_batch_args_missing_video() -> None:
    args = Namespace(
        video=["nonexistent.mp4"],
        cookies=None,
        username=None,
        password=None,
        schedule_from=None,
        schedule_interval=1440,
        timezone=COPENHAGEN,
    )
    with pytest.raises(FileNotFoundError):
        validate_batch_args(args)


def test_validate_batch_args_cookies_and_credentials_conflict() -> None:
    args = Namespace(
        video=[FILENAME],
        cookies="cookies.txt",
        username="user",
        password=None,
        schedule_from=None,
        schedule_interval=1440,
        timezone=COPENHAGEN,
    )
    with pytest.raises(ValueError, match="cannot pass both"):
        validate_batch_args(args)


def test_validate_batch_args_unknown_timezone() -> None:
    args = Namespace(
        video=[FILENAME],
        cookies=None,
        username=None,
        password=None,
        schedule_from="2026-03-24 10:00",
        schedule_interval=1440,
        timezone="Invalid/Timezone",
    )
    with pytest.raises(ValueError, match="Unknown timezone"):
        validate_batch_args(args)


# ---------------------------------------------------------------------------
# validate_batch_args – 10-day limit pre-check (times entered in Copenhagen tz)
# ---------------------------------------------------------------------------


@freeze_time("2026-03-23 12:00")  # UTC
def test_validate_batch_args_schedule_within_limit() -> None:
    """3 videos × 1440 min from 2026-03-23 14:00 Copenhagen (13:00 UTC) → within 10 days."""
    args = Namespace(
        video=[FILENAME, FILENAME, FILENAME],
        cookies=None,
        username=None,
        password=None,
        schedule_from="2026-03-23 14:00",  # Copenhagen CET+1 → 13:00 UTC
        schedule_interval=1440,
        timezone=COPENHAGEN,
    )
    validate_batch_args(args)  # should not raise


@freeze_time("2026-03-23 12:00")  # UTC
def test_validate_batch_args_schedule_exceeds_10_days() -> None:
    """10 videos × 1 day from 2026-03-25 12:00 Copenhagen → last video 2026-04-03 → fail."""
    args = Namespace(
        video=[FILENAME] * 10,
        cookies=None,
        username=None,
        password=None,
        schedule_from="2026-03-25 12:00",  # Copenhagen CET+1 → 11:00 UTC
        schedule_interval=1440,
        timezone=COPENHAGEN,
    )
    with pytest.raises(ValueError, match="10-day limit"):
        validate_batch_args(args)


@freeze_time("2026-03-23 12:00")  # UTC
def test_validate_batch_args_single_video_at_limit_edge() -> None:
    """Single video at 2026-04-02 11:55 Copenhagen (CEST+2 → 09:55 UTC) is within 10 days."""
    args = Namespace(
        video=[FILENAME],
        cookies=None,
        username=None,
        password=None,
        schedule_from="2026-04-02 11:55",  # CEST+2 → 09:55 UTC; max = 2026-04-02 12:00 UTC
        schedule_interval=1440,
        timezone=COPENHAGEN,
    )
    validate_batch_args(args)  # should not raise


# ---------------------------------------------------------------------------
# parse_schedule round-trip
# ---------------------------------------------------------------------------


def test_parse_schedule_valid() -> None:
    result = parse_schedule("2026-03-20 10:00")
    assert result == datetime.datetime(2026, 3, 20, 10, 0)


def test_parse_schedule_none() -> None:
    assert parse_schedule(None) is None
