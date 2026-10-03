import pytest
from toa.stars import Z95, star_rating, stars_config_from_env

SD = 1.5
# Width of one half-star bin, in score units.
BIN = 0.4 * Z95 * SD
EPS = 1e-9


# ── star_rating: anchors ─────────────────────────────────────────────────────


def test_zero_is_three_and_a_half_stars():
    assert star_rating(0.0, SD) == 3.5


def test_zero_is_the_midpoint_of_the_three_and_a_half_bin():
    # The 3.5 bin is [-BIN/2, BIN/2): symmetric about 0.
    assert star_rating(BIN / 2 - EPS, SD) == 3.5
    assert star_rating(BIN / 2 + EPS, SD) == 4.0
    assert star_rating(-BIN / 2 + EPS, SD) == 3.5
    assert star_rating(-BIN / 2 - EPS, SD) == 3.0


def test_five_stars_starts_at_the_prior_95th_percentile():
    threshold = Z95 * SD
    assert star_rating(threshold + EPS, SD) == 5.0
    assert star_rating(threshold - EPS, SD) == 4.5


def test_bottom_five_percent_is_at_most_two_stars():
    # The bins are symmetric about 0, so the mirror of the 5-star threshold
    # falls at the top of the 2-star bin.
    assert star_rating(-Z95 * SD - EPS, SD) == 2.0
    assert star_rating(-Z95 * SD + EPS, SD) == 2.5


@pytest.mark.parametrize("k", range(-7, 4))
def test_every_bin_is_one_half_star_wide(k):
    # Bin k starts at (k - 0.5) * BIN and rates 3.5 + k / 2.
    lower = (k - 0.5) * BIN
    assert star_rating(lower + EPS, SD) == 3.5 + k / 2
    assert star_rating(lower + BIN - EPS, SD) == 3.5 + k / 2


def test_ratings_are_half_star_steps():
    for i in range(-100, 101):
        stars = star_rating(i / 20, SD)
        assert stars * 2 == int(stars * 2)


def test_accepts_decimal_like_scores():
    # DynamoDB hands scores back as Decimals.
    from decimal import Decimal

    assert star_rating(Decimal("0.304"), SD) == 3.5


# ── star_rating: truncation ──────────────────────────────────────────────────


def test_large_positive_score_clamps_to_five():
    assert star_rating(10.0, SD) == 5.0


def test_large_positive_score_unclamped_exceeds_five():
    assert star_rating(10.0, SD, truncate=False) > 5.0
    # 5.5 starts one bin above the 5-star threshold.
    assert star_rating(Z95 * SD + BIN + EPS, SD, truncate=False) == 5.5


def test_large_negative_score_clamps_to_zero():
    assert star_rating(-20.0, SD) == 0.0


def test_large_negative_score_unclamped_goes_below_zero():
    assert star_rating(-20.0, SD, truncate=False) < 0.0


def test_truncation_does_not_touch_in_range_ratings():
    for score in (-3.0, -1.0, 0.0, 1.0, 2.0):
        assert star_rating(score, SD) == star_rating(score, SD, truncate=False)


# ── star_rating: sd ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("sd", [0.5, 1.0, 1.5, 3.0])
def test_bins_scale_with_sd(sd):
    assert star_rating(0.0, sd) == 3.5
    assert star_rating(Z95 * sd + EPS, sd) == 5.0
    assert star_rating(Z95 * sd - EPS, sd) == 4.5


def test_same_score_rates_lower_under_a_wider_prior():
    assert star_rating(2.0, 1.0) == 5.0
    assert star_rating(2.0, 3.0) == 4.0


# ── stars_config_from_env ────────────────────────────────────────────────────


def test_config_reads_sd_and_defaults_truncate_on(monkeypatch):
    monkeypatch.setenv("SD", "1.5")
    monkeypatch.delenv("TRUNCATE_STARS", raising=False)
    assert stars_config_from_env() == (1.5, True)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("false", False),
        ("False", False),
        ("0", False),
        (" false ", False),
    ],
)
def test_config_parses_truncate(monkeypatch, raw, expected):
    monkeypatch.setenv("SD", "1.5")
    monkeypatch.setenv("TRUNCATE_STARS", raw)
    assert stars_config_from_env() == (1.5, expected)


def test_config_rejects_an_unrecognised_truncate_value(monkeypatch):
    monkeypatch.setenv("SD", "1.5")
    monkeypatch.setenv("TRUNCATE_STARS", "yes")
    with pytest.raises(ValueError):
        stars_config_from_env()


def test_config_requires_sd(monkeypatch):
    monkeypatch.delenv("SD", raising=False)
    with pytest.raises(KeyError):
        stars_config_from_env()
