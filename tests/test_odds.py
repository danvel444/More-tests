"""Sanity checks: the analytically-derived odds in lottery/odds.py must
reproduce the well-known published jackpot odds for each game. If someone
edits games.py and breaks the combinatorics, this should fail loudly."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lottery.games import LOTTO_649, LOTTO_MAX, DAILY_GRAND
from lottery.odds import jackpot_odds, odds_table


def test_649_jackpot_odds():
    assert math.isclose(1 / jackpot_odds(LOTTO_649), 13_983_816, rel_tol=1e-9)


def test_max_jackpot_odds():
    assert math.isclose(1 / jackpot_odds(LOTTO_MAX), 133_784_560, rel_tol=1e-9)


def test_grand_jackpot_odds():
    assert math.isclose(1 / jackpot_odds(DAILY_GRAND), 13_348_188, rel_tol=1e-9)


def test_tier_probabilities_sum_le_one():
    for game in (LOTTO_649, LOTTO_MAX, DAILY_GRAND):
        total = sum(r["probability"] for r in odds_table(game))
        assert 0 < total < 1


def test_649_match4_odds_matches_published():
    # Published: 1 in 1,032.4
    row = next(r for r in odds_table(LOTTO_649) if r["tier"] == "Match 4")
    assert math.isclose(row["one_in"], 1032.4, rel_tol=1e-3)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"OK  {name}")
