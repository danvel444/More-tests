"""
Exact combinatorial ("analytic") odds for every prize tier of every game.

These are derived from first principles (hypergeometric counting), not
copied from a website, so they self-validate: the jackpot-tier odds this
module computes must equal the well-known published jackpot odds
(1 in 13,983,816 for 6/49; 1 in 133,784,560 for the new 7/52 Lotto Max
matrix; 1 in 13,348,188 for Daily Grand). tests/test_odds.py checks this.

Two draw models are supported:

  * "bonus" games (6/49, Lotto Max): the main draw picks `pick_count`
    numbers from `pool_size`; a separate bonus ball is then drawn from the
    remaining `pool_size - pick_count` numbers. A ticket can match some of
    the main numbers *and separately* hold the bonus number among its
    non-matching numbers.

  * "grand number" games (Daily Grand): the main draw is a plain
    hypergeometric draw with no bonus ball, plus a fully independent
    uniform draw of a "Grand Number" from 1..grand_range that a ticket
    either matches or doesn't, independent of the main draw.
"""
from __future__ import annotations

from math import comb
from typing import Optional

from .games import Game


def prob_match_bonus_game(pool_size: int, pick_count: int, matches: int,
                           bonus: Optional[bool]) -> float:
    """P(ticket matches exactly `matches` main numbers [and holds/doesn't hold
    the bonus number], bonus/-`pool_size - pick_count` model)."""
    total = comb(pool_size, pick_count)
    leftover = pick_count - matches
    if bonus is None:
        ways = comb(pick_count, matches) * comb(pool_size - pick_count, leftover)
    elif bonus is True:
        if leftover < 1:
            return 0.0
        ways = comb(pick_count, matches) * comb(pool_size - pick_count - 1, leftover - 1)
    else:  # bonus is False
        ways = comb(pick_count, matches) * comb(pool_size - pick_count - 1, leftover)
    return ways / total


def prob_match_grand_game(pool_size: int, pick_count: int, matches: int,
                           grand_range: int, grand: Optional[bool]) -> float:
    """Daily-Grand-style: ordinary hypergeometric main match, independent
    Grand Number draw."""
    total = comb(pool_size, pick_count)
    ways = comb(pick_count, matches) * comb(pool_size - pick_count, pick_count - matches)
    p_main = ways / total
    if grand is None:
        return p_main
    p_grand = (1 / grand_range) if grand else (1 - 1 / grand_range)
    return p_main * p_grand


def tier_probability(game: Game, matches: int, bonus: Optional[bool]) -> float:
    if game.grand_range is not None:
        return prob_match_grand_game(game.pool_size, game.pick_count, matches,
                                      game.grand_range, bonus)
    return prob_match_bonus_game(game.pool_size, game.pick_count, matches, bonus)


def jackpot_odds(game: Game) -> float:
    """Returns 1/N: the probability a single line wins the top prize."""
    return tier_probability(game, game.pick_count, True if game.grand_range else None)


def odds_table(game: Game) -> list[dict]:
    rows = []
    for tier in game.prize_tiers:
        p = tier_probability(game, tier.match_main, tier.bonus)
        rows.append({
            "tier": tier.name,
            "probability": p,
            "one_in": (1 / p) if p > 0 else float("inf"),
            "prize_type": tier.prize_type,
            "amount": tier.amount,
        })
    return rows


def overall_win_probability(game: Game) -> float:
    return sum(r["probability"] for r in odds_table(game))
