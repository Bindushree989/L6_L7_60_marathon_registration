
import pytest

from marathon_registration import entry_fee, start_wave, finisher_status


# ---------- entry_fee tests ----------

def test_entry_fee_all_race_types():
    assert entry_fee("5k", 30, False, False) == 500
    assert entry_fee("10k", 30, False, False) == 800
    assert entry_fee("half", 30, False, False) == 1200
    assert entry_fee("full", 30, False, False) == 1800


def test_entry_fee_early_bird_discount():
    assert entry_fee("5k", 30, True, False) == 375
    assert entry_fee("10k", 30, True, False) == 600


def test_entry_fee_senior_discount():
    assert entry_fee("5k", 65, False, False) == 250
    assert entry_fee("10k", 70, False, False) == 400


def test_entry_fee_tshirt_addition():
    assert entry_fee("5k", 30, False, True) == 800


def test_entry_fee_combined_discounts_and_tshirt():
    # 10k: 800 - 25% = 600; senior discount = 300; T-shirt = 600
    assert entry_fee("10k", 65, True, True) == 600


@pytest.mark.parametrize("race", ["unknown", "marathon", ""])
def test_entry_fee_unknown_race(race):
    with pytest.raises(ValueError, match="unknown race"):
        entry_fee(race, 30, False, False)


@pytest.mark.parametrize("age", [0, 11])
def test_entry_fee_too_young(age):
    with pytest.raises(ValueError, match="too young"):
        entry_fee("5k", age, False, False)


@pytest.mark.parametrize("race", ["half", "full"])
@pytest.mark.parametrize("age", [12, 17])
def test_entry_fee_age_restriction_for_long_races(race, age):
    with pytest.raises(ValueError, match="too young for this distance"):
        entry_fee(race, age, False, False)


def test_entry_fee_age_18_allowed_for_half():
    assert entry_fee("half", 18, False, False) == 1200


def test_entry_fee_age_12_allowed_for_5k():
    assert entry_fee("5k", 12, False, False) == 500


# ---------- start_wave tests ----------

def test_start_wave_none_time():
    assert start_wave(None, "full") == "D"
    assert start_wave(None, "5k") == "D"


def test_start_wave_group_a():
    assert start_wave(90, "5k") == "A"
    assert start_wave(180, "full") == "A"


def test_start_wave_group_b():
    assert start_wave(120, "5k") == "B"
    assert start_wave(240, "full") == "B"


def test_start_wave_group_c():
    assert start_wave(121, "5k") == "C"
    assert start_wave(241, "full") == "C"


def test_start_wave_cutoff_boundary():
    assert start_wave(90, "5k") == "A"
    assert start_wave(91, "5k") == "B"


# ---------- finisher_status tests ----------

def test_finisher_disqualified_for_missed_checkpoint():
    assert finisher_status(60, "5k", 1) == "DSQ"
    assert finisher_status(400, "full", 2) == "DSQ"


def test_finisher_status_5k_and_10k():
    assert finisher_status(90, "5k", 0) == "finisher"
    assert finisher_status(91, "5k", 0) == "DNF"
    assert finisher_status(90, "10k", 0) == "finisher"


def test_finisher_status_half():
    assert finisher_status(180, "half", 0) == "finisher"
    assert finisher_status(181, "half", 0) == "DNF"


def test_finisher_status_full():
    assert finisher_status(360, "full", 0) == "finisher"
    assert finisher_status(361, "full", 0) == "DNF"


def test_finisher_status_unknown_race_uses_default_limit():
    assert finisher_status(90, "unknown", 0) == "finisher"
    assert finisher_status(91, "unknown", 0) == "DNF"
