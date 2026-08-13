"""
Game definitions for the three Canadian lotteries under study.

Odds are computed analytically (see lottery/odds.py) from each game's
combinatorial structure -- they are not hand-typed from a website, so they
can't drift from the actual rules encoded here. Dollar prize amounts for
fixed-payout tiers, and the ticket price / pool size / matrix, are sourced
from the lottery operators' public game-condition documents as of Aug 2026:

  - Lotto 6/49:  WCLC / OLG / Loto-Québec game rules & prize structure PDF
  - Lotto Max:   BCLC "Lotto Max Game Conditions" (approved Sep 25, 2025,
                 in effect Apr 10, 2026) -- 7/52 matrix, $6 per 4 lines
  - Daily Grand: WCLC / ALC game rules & prize structure

Pari-mutuel ("Prize fund") tiers do not have a fixed dollar value -- the
amount depends on total ticket sales for that specific draw and is split
among everyone who hits that tier. We deliberately do NOT invent a dollar
figure for those tiers; the simulator treats them as "prize_type=parimutuel"
and excludes them from dollar-EV math unless a typical/illustrative value is
explicitly supplied. Where a lottery publishes a guaranteed minimum (Daily
Grand's life-annuity lump-sum minimums), we use that published minimum.

This is a best-effort model for simulation and education purposes, not a
substitute for the operator's current official rules -- always check
wclc.com / olg.ca / lotoquebec.com / alc.ca / bclc.com for the numbers that
apply to an actual purchase decision.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class PrizeTier:
    name: str
    match_main: int                 # numbers matched out of the main draw
    bonus: Optional[bool] = None    # None = irrelevant, True/False = must (not) match bonus/grand
    prize_type: str = "fixed"       # "fixed" | "parimutuel" | "jackpot"
    amount: Optional[float] = None  # dollars, only meaningful for fixed/illustrative tiers


@dataclass(frozen=True)
class Game:
    key: str
    display_name: str
    pool_size: int             # size of the main number pool
    pick_count: int            # how many main numbers a ticket/draw selects
    has_bonus: bool            # bonus ball drawn from the pool *not* chosen in the main draw
    grand_range: Optional[int] # Daily Grand's independent 1..N "Grand Number"; None otherwise
    ticket_price: float        # price of one purchasable play, as sold
    lines_per_ticket: int      # number of number-lines that price buys
    jackpot_typical: float     # a representative jackpot size, used only for illustrative EV
    prize_tiers: tuple = field(default_factory=tuple)

    # --- Rollover dynamics (used only by the rollover-chasing experiment,
    # simulate.py:rollover_chase_test). None for games whose top prize is a
    # fixed annuity rather than a pari-mutuel jackpot that rolls over --
    # Daily Grand's "$1,000/day for life" doesn't grow when unwon, so
    # "chasing" it is not a meaningful strategy and these are left unset.
    # All four values below are illustrative assumptions -- the operators
    # do not publish an exact jackpot-growth-per-draw or sales-vs-jackpot
    # curve -- see the rollover_chase_test docstring for how they're used.
    jackpot_reset: Optional[float] = None      # jackpot value right after a win
    jackpot_cap: Optional[float] = None        # ceiling (Lotto Max is capped by rule)
    jackpot_increment: Optional[float] = None  # assumed $ growth per unwon draw
    sales_base: Optional[int] = None           # assumed # of tickets in play at jackpot_reset
    sales_elasticity: Optional[float] = None   # how ticket sales grow as the jackpot grows:
                                                # sales(J) = sales_base * (J / jackpot_reset) ** elasticity

    @property
    def price_per_line(self) -> float:
        return self.ticket_price / self.lines_per_ticket


LOTTO_649 = Game(
    key="649",
    display_name="Lotto 6/49",
    pool_size=49,
    pick_count=6,
    has_bonus=True,
    grand_range=None,
    ticket_price=3.00,
    lines_per_ticket=1,
    jackpot_typical=12_000_000,  # user-specified illustrative snapshot for the sharing experiment
    prize_tiers=(
        PrizeTier("Match 6 (Jackpot)", 6, None, "jackpot"),
        PrizeTier("Match 5 + Bonus", 5, True, "parimutuel"),
        PrizeTier("Match 5", 5, False, "parimutuel"),
        PrizeTier("Match 4", 4, None, "fixed", 25.0),
        PrizeTier("Match 3", 3, None, "fixed", 10.0),
        PrizeTier("Match 2 + Bonus", 2, True, "fixed", 5.0),  # free play
    ),
    jackpot_reset=5_000_000,       # published starting/reset jackpot
    jackpot_cap=None,              # no hard cap; 6/49 jackpots have run past $70M unwon
    jackpot_increment=3_000_000,   # illustrative avg growth per unwon draw (2 draws/week)
    sales_base=6_000_000,          # same illustrative baseline as the sharing experiment
    sales_elasticity=1.3,          # sales grow faster than linearly as the jackpot grows
)

LOTTO_MAX = Game(
    key="max",
    display_name="Lotto Max",
    pool_size=52,               # matrix widened 50->52 effective Apr 10, 2026
    pick_count=7,
    has_bonus=True,
    grand_range=None,
    ticket_price=6.00,          # widened matrix also raised price 5->6
    lines_per_ticket=4,         # ...and lines per play 3->4
    jackpot_typical=40_000_000,  # user-specified illustrative snapshot for the sharing experiment
    prize_tiers=(
        PrizeTier("Match 7 (Jackpot)", 7, None, "jackpot"),
        PrizeTier("Match 6 + Bonus", 6, True, "parimutuel"),
        PrizeTier("Match 6", 6, False, "parimutuel"),
        PrizeTier("Match 5 + Bonus", 5, True, "parimutuel"),
        PrizeTier("Match 5", 5, False, "parimutuel"),
        PrizeTier("Match 4 + Bonus", 4, True, "parimutuel"),
        PrizeTier("Match 4", 4, False, "fixed", 20.0),
        PrizeTier("Match 3 + Bonus", 3, True, "fixed", 20.0),
        PrizeTier("Match 3", 3, False, "fixed", 5.0),  # free play
    ),
    jackpot_reset=10_000_000,      # published starting/reset jackpot
    jackpot_cap=90_000_000,        # published cap effective Apr 10, 2026
    jackpot_increment=4_000_000,   # illustrative avg growth per unwon draw (2 draws/week)
    sales_base=10_000_000,         # same illustrative baseline as the sharing experiment
    sales_elasticity=1.3,          # sales grow faster than linearly as the jackpot grows
)

DAILY_GRAND = Game(
    key="grand",
    display_name="Daily Grand",
    pool_size=49,
    pick_count=5,
    has_bonus=False,
    grand_range=7,               # independent "Grand Number" 1-7
    ticket_price=3.00,
    lines_per_ticket=1,
    jackpot_typical=7_000_000,   # published minimum lump-sum guarantee for the annuity jackpot
    prize_tiers=(
        PrizeTier("Match 5 + Grand (Jackpot: $1,000/day for life)", 5, True, "jackpot", 7_000_000),
        PrizeTier("Match 5 ($25,000/year for life)", 5, False, "fixed", 500_000),
        PrizeTier("Match 4 + Grand", 4, True, "fixed", 1_000.0),
        PrizeTier("Match 4", 4, False, "fixed", 500.0),
        PrizeTier("Match 3 + Grand", 3, True, "fixed", 100.0),
        PrizeTier("Match 3", 3, False, "fixed", 20.0),
        PrizeTier("Match 2 + Grand", 2, True, "fixed", 10.0),
        PrizeTier("Match 1 + Grand", 1, True, "fixed", 4.0),
        PrizeTier("Grand Number only", 0, True, "fixed", 4.0),  # free play, valued at ticket price
    ),
)

ALL_GAMES = {g.key: g for g in (LOTTO_649, LOTTO_MAX, DAILY_GRAND)}
