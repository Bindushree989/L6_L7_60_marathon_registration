
import pytest

from marathon_registration import entry_fee, start_wave, finisher_status


# ---------- entry_fee: every decision outcome ----------

def test_entry_fee_race_validation():
    with pytest.raises(ValueError, match="unknown race"):
        entry_fee("invalid", 30, False, False)

    assert entry_fee("5k", 30, False, False) == 500


def test_entry_fee_minimum_age_decision():
    with pytest.raises(ValueError, match="too young"):
        entry_fee("5k", 11, False, False)

    assert entry_fee("5k", 12, False, False) == 500


@pytest.mark.parametrize("race", ["half", "full"])
def test_entry_fee_long_race_age_decision(race):
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee(race, 17, False, False)

    assert entry_fee(race, 18, False, False) > 0


def test_entry_fee_short_race_age_decision():
    assert entry_fee("10k", 17, False, False) == 800


def test_entry_fee_early_bird_both_outcomes():
    assert entry_fee("5k", 30, False, False) == 500
    assert entry_fee("5k", 30, True, False) == 375


def test_entry_fee_senior_both_outcomes():
    assert entry_fee("5k", 64, False, False) == 500
    assert entry_fee("5k", 65, False, False) == 250


def test_entry_fee_tshirt_both_outcomes():
    assert entry_fee("5k", 30, False, False) == 500
    assert entry_fee("5k", 30, False, True) == 800


def test_entry_fee_combined_conditions():
    assert entry_fee("10k", 65, True, True) == 600


# ---------- start_wave: every decision outcome ----------

def test_start_wave_missing_time():
    assert start_wave(None, "full") == "D"


@pytest.mark.parametrize(
    "race,time,expected",
    [
        ("full", 180, "A"),
        ("full", 181, "B"),
        ("full", 240, "B"),
        ("full", 241, "C"),
        ("5k", 90, "A"),
        ("5k", 91, "B"),
        ("5k", 120, "B"),
        ("5k", 121, "C"),
        ("half", 90, "A"),
        ("half", 121, "C"),
    ],
)
def test_start_wave_time_branches(race, time, expected):
    assert start_wave(time, race) == expected


# ---------- finisher_status: every decision outcome ----------

def test_finisher_checkpoint_decision():
    assert finisher_status(60, "5k", 0) == "finisher"
    assert finisher_status(60, "5k", 1) == "DSQ"


@pytest.mark.parametrize(
    "race,limit",
    [
        ("full", 360),
        ("half", 180),
        ("5k", 90),
        ("10k", 90),
        ("unknown", 90),
    ],
)
def test_finisher_time_limit_branches(race, limit):
    assert finisher_status(limit, race, 0) == "finisher"
    assert finisher_status(limit + 1, race, 0) == "DNF"


def test_finisher_checkpoint_takes_priority():
    assert finisher_status(999, "full", 1) == "DSQ"
