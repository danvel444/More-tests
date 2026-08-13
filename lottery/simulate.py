"""
The five Monte Carlo experiments behind the strategy comparison:

  A. fairness_test        -- does playing fixed numbers vs. quick-pick
                              change your odds of hitting any given prize
                              tier?  (Answer should be: no, within noise.)

  B. jackpot_sharing_test  -- if you DO hit the jackpot, does the choice of
                              numbers change how many other people you're
                              statistically likely to split it with?
                              (This is where a real edge exists.)

  C. wheel_test            -- does a "wheeling system" (buying every
                              combination within a chosen subset of numbers)
                              beat buying the same number of independent
                              random lines?

  D. ticket_count_scaling  -- does buying more lines per draw (or pooling
                              into a syndicate) change your return per
                              dollar spent?

  E. rollover_chase_test   -- "only play when the jackpot is big" -- does
                              chasing large rollovers actually raise your
                              return per dollar once you account for the
                              extra ticket sales (and therefore extra
                              jackpot-sharing risk) that a big jackpot
                              itself attracts?

Each function runs a real Monte Carlo simulation (not just the closed-form
odds) so results carry authentic sampling noise -- exactly what you'd see
running the experiment for real.
"""
from __future__ import annotations

from math import comb
from typing import Optional

import numpy as np
import pandas as pd

from .games import Game
from .odds import odds_table, jackpot_odds
from . import strategies as strat


def _tier_hits(game: Game, main_matches: np.ndarray, holds_bonus: Optional[np.ndarray],
               grand_hit: Optional[np.ndarray]) -> dict:
    """Given per-draw match counts (and bonus/grand hit flags), tally how
    many draws landed in each official prize tier."""
    counts = {}
    for tier in game.prize_tiers:
        mask = main_matches == tier.match_main
        if tier.bonus is not None:
            if game.grand_range is not None:
                mask = mask & (grand_hit == tier.bonus)
            else:
                mask = mask & (holds_bonus == tier.bonus)
        counts[tier.name] = int(mask.sum())
    return counts


def _match_and_bonus(game: Game, draws: dict, ticket_main: np.ndarray,
                      ticket_grand: Optional[np.ndarray]):
    main_matches = (draws["main_bool"] * ticket_main).sum(axis=1)
    holds_bonus = None
    if game.has_bonus:
        n = draws["main_bool"].shape[0]
        bidx = draws["bonus_idx"]
        if ticket_main.ndim == 1:
            holds_bonus = ticket_main[bidx] == 1
        else:
            holds_bonus = ticket_main[np.arange(n), bidx] == 1
    grand_hit = None
    if game.grand_range is not None:
        if np.isscalar(ticket_grand):
            grand_hit = draws["grand"] == ticket_grand
        else:
            grand_hit = draws["grand"] == ticket_grand
    return main_matches, holds_bonus, grand_hit


# ---------------------------------------------------------------------------
# A. Fairness test: fixed numbers vs. quick pick
# ---------------------------------------------------------------------------

def fairness_test(game: Game, n_draws: int, n_fixed_players: int = 25,
                   seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    draws = strat.simulate_draws(game, n_draws, rng)

    theory = {r["tier"]: r["probability"] for r in odds_table(game)}

    rows = []

    # Quick pick: a fresh random ticket every single draw.
    qp = strat.quick_pick_tickets(game, n_draws, rng)
    mm, hb, gh = _match_and_bonus(game, draws, qp["main_bool"], qp["grand"])
    hits = _tier_hits(game, mm, hb, gh)
    for tier, h in hits.items():
        rows.append({"strategy": "Quick Pick", "player": "quick_pick", "tier": tier,
                      "hits": h, "n_draws": n_draws,
                      "empirical_prob": h / n_draws, "theoretical_prob": theory[tier]})

    # Fixed numbers: N different simulated players, each locks in one set of
    # numbers for all n_draws draws. This also shows that any *one* fixed
    # player's results are just as noisy as quick pick -- "my numbers are
    # hot/cold" is sampling variance, not signal.
    for p in range(n_fixed_players):
        ticket = strat.fixed_ticket(game, rng)
        mm, hb, gh = _match_and_bonus(game, draws, ticket["main_bool"], ticket["grand"])
        hits = _tier_hits(game, mm, hb, gh)
        for tier, h in hits.items():
            rows.append({"strategy": "Fixed Numbers", "player": f"fixed_{p}", "tier": tier,
                         "hits": h, "n_draws": n_draws,
                         "empirical_prob": h / n_draws, "theoretical_prob": theory[tier]})

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# B. Jackpot-sharing test: does picking "popular" numbers cost you EV?
# ---------------------------------------------------------------------------

def expected_co_winners(game: Game, m_other_players: int, f_calendar: float,
                         ticket_all_le_31: bool) -> float:
    """Expected number of *other* players who independently hold the exact
    same winning combination as you, under a simple two-population model:

      - a fraction `f_calendar` of all players restrict themselves entirely
        to numbers 1-31 (birthday-style picking) and choose uniformly among
        those C(31, pick_count) combinations;
      - everyone else (quick pick + unrestricted self-pickers) chooses
        uniformly among all C(pool_size, pick_count) combinations.

    This is an illustrative model of a real, well-documented human bias
    (over-selection of calendar-range numbers), not a precise measurement of
    actual player behaviour -- treat f_calendar and m_other_players as
    adjustable assumptions.
    """
    k = game.pick_count
    c_full = comb(game.pool_size, k)
    c_calendar = comb(min(31, game.pool_size), k)
    if ticket_all_le_31:
        p_match = f_calendar / c_calendar + (1 - f_calendar) / c_full
    else:
        p_match = (1 - f_calendar) / c_full
    return m_other_players * p_match


def jackpot_sharing_test(game: Game, m_other_players: int, f_calendar: float,
                          jackpot: float, n_trials: int = 20_000, seed: int = 0) -> pd.DataFrame:
    """Monte Carlo: *conditional on having won the jackpot*, how many people
    would you be splitting it with, and what's your expected payout, under
    each number-choice pattern? Poisson sampling is the correct model here
    because m_other_players is large and the per-person match probability is
    tiny (the Poisson limit of a Binomial)."""
    rng = np.random.default_rng(seed)
    scenarios = {
        "Popular / calendar numbers (all ≤ 31)": True,
        "Quick pick / spread numbers (≥ 1 number > 31)": False,
    }
    rows = []
    for label, all_le_31 in scenarios.items():
        lam = expected_co_winners(game, m_other_players, f_calendar, all_le_31)
        co_winners = rng.poisson(lam, size=n_trials)
        payout = jackpot / (1 + co_winners)
        rows.append({
            "scenario": label,
            "expected_co_winners": lam,
            "mean_co_winners_sim": co_winners.mean(),
            "mean_payout_sim": payout.mean(),
            "median_payout_sim": np.median(payout),
            "p_share_with_anyone": (co_winners > 0).mean(),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# C. Wheeling systems vs. the same number of independent random lines
# ---------------------------------------------------------------------------

def _prize_value_for_matches(game: Game, main_matches: np.ndarray,
                              holds_bonus: Optional[np.ndarray]) -> np.ndarray:
    """Dollar value per line per draw, fixed-prize tiers only (parimutuel /
    jackpot tiers are excluded from this $ sum since they have no single
    fixed value -- see games.py docstring)."""
    value = np.zeros(main_matches.shape[0], dtype=float)
    for tier in game.prize_tiers:
        if tier.prize_type != "fixed" or tier.amount is None:
            continue
        mask = main_matches == tier.match_main
        if tier.bonus is not None and holds_bonus is not None:
            mask = mask & (holds_bonus == tier.bonus)
        value[mask] += tier.amount
    return value


def wheel_test(game: Game, wheel_pool_size: int, n_draws: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    draws = strat.simulate_draws(game, n_draws, rng)

    pool_numbers = rng.choice(game.pool_size, size=wheel_pool_size, replace=False)
    wheel_lines = strat.full_wheel(game, pool_numbers)
    n_lines = wheel_lines.shape[0]

    # Random lines of the same count, for a fair $-for-$ comparison.
    random_lines = np.array([
        strat.random_combo_bool(game.pool_size, game.pick_count, rng) for _ in range(n_lines)
    ])

    def total_return_per_draw(lines: np.ndarray) -> np.ndarray:
        total = np.zeros(n_draws, dtype=float)
        for i in range(lines.shape[0]):
            mm, hb, _ = _match_and_bonus(game, draws, lines[i], None)
            total += _prize_value_for_matches(game, mm, hb)
        return total

    wheel_return = total_return_per_draw(wheel_lines)
    random_return = total_return_per_draw(random_lines)
    cost_per_draw = n_lines * game.price_per_line

    return pd.DataFrame([
        {"method": f"Full wheel ({wheel_pool_size} numbers, {n_lines} lines)",
         "lines": n_lines, "cost_per_draw": cost_per_draw,
         "mean_return_per_draw": wheel_return.mean(),
         "return_per_dollar": wheel_return.mean() / cost_per_draw},
        {"method": f"{n_lines} independent random lines",
         "lines": n_lines, "cost_per_draw": cost_per_draw,
         "mean_return_per_draw": random_return.mean(),
         "return_per_dollar": random_return.mean() / cost_per_draw},
    ])


# ---------------------------------------------------------------------------
# D. More tickets / syndicates: does volume change return-per-dollar?
# ---------------------------------------------------------------------------

def ticket_count_scaling(game: Game, line_counts: list[int], n_draws: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    draws = strat.simulate_draws(game, n_draws, rng)
    rows = []
    for k in line_counts:
        total = np.zeros(n_draws, dtype=float)
        for _ in range(k):
            qp = strat.quick_pick_tickets(game, n_draws, rng)
            mm, hb, gh = _match_and_bonus(game, draws, qp["main_bool"], qp["grand"])
            total += _prize_value_for_matches(game, mm, hb)
        cost_per_draw = k * game.price_per_line
        rows.append({
            "lines_per_draw": k,
            "cost_per_draw": cost_per_draw,
            "mean_fixed_prize_return_per_draw": total.mean(),
            "return_per_dollar": total.mean() / cost_per_draw,
            "std_return_per_draw": total.std(),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# E. Rollover chasing: is a bigger jackpot actually a bigger edge?
# ---------------------------------------------------------------------------

def fixed_tier_ev_per_line(game: Game) -> float:
    """Expected $ return per line per draw from the fixed-dollar tiers only
    (excludes the jackpot and any parimutuel tiers, which are handled
    separately)."""
    from .odds import tier_probability
    total = 0.0
    for tier in game.prize_tiers:
        if tier.prize_type == "fixed" and tier.amount:
            total += tier.amount * tier_probability(game, tier.match_main, tier.bonus)
    return total


def simulate_jackpot_trajectory(game: Game, n_draws: int, rng: np.random.Generator) -> pd.DataFrame:
    """Simulate one long, single Markov chain of `n_draws` consecutive
    draws of `game`'s pari-mutuel jackpot: it resets to `jackpot_reset`
    whenever *someone* (not necessarily you) wins it, and otherwise grows by
    `jackpot_increment` per draw up to `jackpot_cap`. The number of *other*
    tickets in play each draw is assumed to scale with the jackpot size
    (`sales_base * (J / jackpot_reset) ** sales_elasticity`) -- bigger
    jackpots sell more tickets, which is well documented directionally, but
    the exact curve is an illustrative assumption (see games.py).

    Because the chain is ergodic, one long trajectory gives the same
    long-run distribution of "what jackpot size was on offer, and how
    crowded was that draw" as averaging many short independent runs would --
    it's just simpler to simulate. Returns one row per simulated draw.
    """
    if game.jackpot_reset is None:
        raise ValueError(f"{game.display_name} has no rollover dynamics configured "
                          f"(its top prize is a fixed annuity, not a rolling jackpot)")

    p_line = jackpot_odds(game)
    cap = game.jackpot_cap if game.jackpot_cap is not None else float("inf")

    jackpot = np.empty(n_draws)
    sales = np.empty(n_draws)
    won = np.empty(n_draws, dtype=bool)

    j = game.jackpot_reset
    for t in range(n_draws):
        m = game.sales_base * (j / game.jackpot_reset) ** game.sales_elasticity
        p_won_by_someone = -np.expm1(-m * p_line)  # 1 - exp(-m*p_line), numerically stable
        w = rng.random() < p_won_by_someone
        jackpot[t], sales[t], won[t] = j, m, w
        j = game.jackpot_reset if w else min(j + game.jackpot_increment, cap)

    return pd.DataFrame({"draw": np.arange(n_draws), "jackpot": jackpot,
                          "other_tickets": sales, "won_by_someone": won})


def rollover_chase_test(game: Game, thresholds: list[float], n_draws: int,
                         f_calendar: float = 0.12, seed: int = 0) -> pd.DataFrame:
    """Compare 'always play' against 'only play when the jackpot is at
    least $threshold' for each threshold, playing a spread/quick-pick-style
    ticket (the strategy shown in experiment B to minimize sharing risk) in
    every case -- isolating the *timing* decision from the *number-choice*
    decision. Return per dollar is computed exactly (closed-form Poisson
    expectation of 1/(1+co-winners), no extra sampling noise) for the
    jackpot component, using each draw's own simulated ticket-sales level;
    the constant fixed-tier EV is added on top.
    """
    rng = np.random.default_rng(seed)
    traj = simulate_jackpot_trajectory(game, n_draws, rng)
    k = game.pick_count
    c_full = comb(game.pool_size, k)
    p_line = jackpot_odds(game)
    fixed_ev = fixed_tier_ev_per_line(game)

    # Spread ticket: never in the calendar-restricted population, so its
    # per-draw expected-co-winners is just other_tickets * (1-f_calendar)/c_full.
    lam = traj["other_tickets"].to_numpy() * (1 - f_calendar) / c_full
    # E[1/(1+X)] for X ~ Poisson(lam), closed form; lam=0 -> 1.
    with np.errstate(divide="ignore", invalid="ignore"):
        e_inv = np.where(lam > 0, -np.expm1(-lam) / lam, 1.0)
    per_draw_jackpot_ev = p_line * traj["jackpot"].to_numpy() * e_inv

    rows = []
    for threshold in thresholds:
        mask = traj["jackpot"].to_numpy() >= threshold
        if mask.sum() == 0:
            continue
        jackpot_component = per_draw_jackpot_ev[mask].mean()
        ev_per_line = jackpot_component + fixed_ev
        rows.append({
            "threshold": threshold,
            "fraction_of_draws_played": mask.mean(),
            "mean_jackpot_when_played": traj["jackpot"].to_numpy()[mask].mean(),
            "mean_other_tickets_when_played": traj["other_tickets"].to_numpy()[mask].mean(),
            "jackpot_ev_per_line": jackpot_component,
            "fixed_tier_ev_per_line": fixed_ev,
            "total_ev_per_line": ev_per_line,
            "return_per_dollar": ev_per_line / game.price_per_line,
        })
    return pd.DataFrame(rows)
