# Canadian Lottery Strategy Simulator

A Monte Carlo environment for testing lottery-playing strategies against
**Lotto 6/49**, **Lotto Max**, and **Daily Grand** — the three games as
currently structured (checked against operator rules current as of Aug
2026; Lotto Max reflects the 7/52-matrix / $6-for-4-lines rules that took
effect April 10, 2026).

## TL;DR — what the simulation found

**Fixed numbers and Quick Pick have *identical* odds of winning, at every
prize tier, in every game.** 2,000,000 simulated draws per game confirm
this to within sampling noise — see `results/fairness_chart.png`. This
isn't really a "finding," it's a mathematical certainty: each draw is an
independent, uniform draw over all possible combinations, so *every*
6/49, 7/52, or 5/49 combination — whether you picked it once and replay
it forever, or get a new random one every time — has exactly the same
probability of being drawn. "My numbers are due" and "quick pick is
luckier" are both the same myth from opposite directions.

**But there is a real, quantifiable edge — it's just not about odds, it's
about what happens *if* you win.** Jackpots (and several of the upper
tiers) are pari-mutuel: split evenly among everyone who matches. Humans
don't pick numbers uniformly — a well-documented bias toward birthdays
means a disproportionate share of manually-chosen tickets cluster
entirely in 1–31. A ticket built entirely from that range is far more
likely to have to share a jackpot than one that includes numbers outside
it (which quick pick does, more or less automatically, since it draws
uniformly across the whole pool). Simulating a simple two-population model
(§B below), at illustrative jackpots of **$12M for 6/49 and $40M for Lotto
Max**:

| Game | Expected payout, "popular" numbers (all ≤ 31) | Expected payout, spread/quick-pick-style numbers | Difference |
|---|---:|---:|---:|
| Lotto 6/49 ($12M jackpot) | $6.58M | $10.00M | **+52%** |
| Lotto Max ($40M jackpot) | $31.15M | $38.73M | **+24%** |
| Daily Grand ($7M jackpot) | $4.13M | $5.61M | **+36%** |

Same odds of winning. Meaningfully different expected *payout* if you do
— and this percentage edge is roughly constant regardless of jackpot size
(it falls out of the sharing math, not the dollar amount), so it holds at
whatever jackpot you're actually looking at.

**Buying more tickets, pooling into a syndicate, or using a "wheeling
system" do not improve your return per dollar** — they scale your
variance (and your chance of winning *something*) but the return per
dollar spent stays flat (§C, §D). A wheel is not a cheat code; it's a
structured way to spend the same money on the same number of random-ish
lines.

**Rollover chasing ("only play when the jackpot is big") has a real, if
modest, edge — and it saturates fast.** §E simulates the actual rollover
dynamics: a jackpot that resets when someone wins it and grows when it
doesn't, with ticket sales assumed to grow *faster than linearly* with the
jackpot (bigger jackpots get more media attention and sell disproportionately
more tickets — a real, documented effect). That second effect eats into
the first, but doesn't cancel it out in this model:

| Game | Always play (reset jackpot) | At the $12M/$40M jackpot | At a big rollover |
|---|---:|---:|---:|
| Lotto 6/49 | 21.2¢ per $1 (~$7.3M avg jackpot) | 26.6¢ per $1 (≥$12M, played 5.3% of draws) | 27.5¢ per $1 (≥$20M, played 0.1% of draws) |
| Lotto Max | 30.8¢ per $1 (~$21.8M avg jackpot) | 39.4¢ per $1 (≥$40M, played 6.5% of draws) | 43.8–46.9¢ per $1 (≥$60–80M, played <0.3% of draws) |

So chasing rollovers is directionally correct advice — but it buys you a
few extra cents on the dollar, not a positive-EV bet, and most of the
available improvement is already captured by the time you get to
"noticeably large" jackpots; waiting for the truly enormous ones barely
moves the number further (see `results/rollover_chart.png`).

**The whole game is negative expected value regardless of strategy** —
this is the largest, systematic finding: even under the most favorable
strategy combination tested (spread numbers + rollover chasing), return
per dollar tops out around 45–47¢ on the dollar for Lotto Max and never
gets past the high-20s¢ for 6/49. No strategy tested — including "pick
different numbers" and "only play the big jackpots" — turns this into a
positive-EV bet. The only lever that matters is *minimizing the cost of
being wrong when you're right*.

## The strategies tested

1. **Fixed numbers** — pick a set once, replay it every draw.
2. **Quick pick** — new random numbers every draw.
3. **"Popular"/calendar numbers** — a set drawn entirely from 1–31 (how
   most people who hand-pick numbers actually choose, per birthday bias).
4. **Deliberately spread/"unpopular" numbers** — numbers chosen only from
   above 31, structurally avoiding the human clustering zone.
5. **More lines per draw / syndicates** — buying k lines instead of 1.
6. **Wheeling systems** — buying every combination within a chosen subset
   of numbers (a "full wheel"), compared dollar-for-dollar against the
   same count of independent random lines.
7. **Rollover chasing** — only buying tickets once the jackpot clears a
   threshold, simulating the actual jackpot-reset/growth/re-sale dynamics
   rather than just plugging in a bigger number by hand.

## How the simulation is built

```
lottery/
  games.py       Game definitions: pool size, pick count, bonus/grand-number
                 rules, ticket price, prize table, and (for 6/49 and Lotto
                 Max) the illustrative rollover-dynamics parameters used by
                 experiment E — all with a citation/assumption trail in the
                 module docstring.
  odds.py        Exact odds for every prize tier, derived analytically from
                 first-principles combinatorics (hypergeometric counting) —
                 not copied from a website. Self-validates against the
                 well-known published jackpot odds (see tests/).
  strategies.py  Ticket/draw generation, vectorized with numpy: every
                 combination is a boolean vector, so "how many numbers
                 does ticket X share with draw Y" is one dot product,
                 applied across millions of draws at once.
  simulate.py    The five Monte Carlo experiments (A-E below).
scripts/
  run_simulation.py   Runs everything for all 3 games, writes results/.
tests/
  test_odds.py   Sanity checks: computed odds must match published odds.
results/
  *.csv, *.png, summary.md   Output of the full run (already generated).
```

### A. Fairness test (`fairness_test`)
2,000,000 simulated draws per game. One "quick pick" player gets a fresh
random ticket every draw; 25 independent "fixed" players each lock in one
ticket for all 2,000,000 draws. Empirical hit rate per tier is compared
against the analytically-exact theoretical probability. Result: all three
lines (fixed / quick pick / theoretical) overlap at every tier, for every
game — see `results/fairness_chart.png`.

### B. Jackpot-sharing model (`jackpot_sharing_test`, `expected_co_winners`)
A simple, explicitly-labeled two-population model: a fraction `f_calendar`
of all other players restrict themselves entirely to numbers 1–31 and
pick uniformly among those combinations; everyone else (quick pick +
unrestricted self-pickers) picks uniformly across the full pool. Given
that model, the expected number of people who'd share your jackpot with
you follows a Poisson distribution (large population, tiny per-person
match probability = the classic Poisson limit), which is what's actually
sampled — 200,000 trials per game. **The `m_other_players` (total tickets
in play), `f_calendar` (12% used here), and `jackpot_typical` ($12M / $40M
/ $7M) values are illustrative assumptions, not measured data** — real
per-draw sales and the exact degree of number-selection bias aren't
published by the lottery corporations. `scripts/run_simulation.py` and
`lottery/games.py` expose these as easy-to-edit constants; the qualitative
result (spread numbers beat calendar numbers, by a roughly constant
percentage regardless of jackpot size) is robust across a wide range of
both.

### C. Wheeling systems (`wheel_test`)
A "full wheel": every combination of the game's pick-count within a
chosen subset of numbers (e.g., all C(9,6)=84 six-number lines from a
9-number pool for 6/49). Compared, dollar for dollar, against the same
number of independent random lines, over 300,000 simulated draws. Result:
statistically indistinguishable return per dollar (e.g., 6/49: wheel
$0.0872/$1 vs random $0.0874/$1) — a wheel changes *which* smaller prizes
you're likely to hit, not your overall expected return.

### D. Ticket-count / syndicate scaling (`ticket_count_scaling`)
1, 5, 20, and 50 quick-pick lines per draw, 300,000 draws. Return per
dollar spent is flat across all four (e.g., 6/49: ~$0.087/$1 regardless of
line count) — buying more tickets (or pooling into a syndicate that buys
more tickets) multiplies your total spend and your variance, not your
per-dollar efficiency.

### E. Rollover chasing (`rollover_chase_test`, `simulate_jackpot_trajectory`)
Unlike A–D, this experiment simulates a *process*, not just independent
draws: one long (1,000,000-draw) Markov chain per game where the jackpot
resets to `jackpot_reset` whenever someone wins it and otherwise grows by
`jackpot_increment` per draw (up to `jackpot_cap`, for Lotto Max), and the
number of *other* tickets in play that draw scales with the jackpot size
as `sales_base * (jackpot / jackpot_reset) ** sales_elasticity`. Because
the chain is ergodic, one long run gives the same long-run distribution as
averaging many short independent runs would.

For each candidate "only play when jackpot ≥ threshold" rule, the expected
return per dollar is computed using every simulated draw that clears the
threshold: the jackpot component uses the *closed-form* expectation
`E[1 / (1 + co-winners)]` for a Poisson-distributed co-winner count (exact,
no extra sampling noise), and the constant fixed-tier EV is added on top.
The ticket is always a spread/quick-pick-style ticket (§B's better
number-choice strategy), so this isolates the *timing* decision.

Daily Grand is excluded from this experiment: its top prize is a fixed
$1,000/day-for-life annuity that doesn't grow when unwon, so "chasing" it
isn't a meaningful strategy in the first place.

**The rollover-growth rate, cap, and — especially — the sales-elasticity
exponent (1.3, meaning sales grow noticeably faster than the jackpot
itself) are illustrative assumptions**, not measured figures; see
`lottery/games.py`. The qualitative result (chasing helps, but with
sharply diminishing returns) is fairly robust to this exponent as long as
it's above 1; an elasticity of exactly 1 (sales scale perfectly
proportionally to the jackpot) would make chasing pointless, and an
elasticity well above 1 (extreme "jackpot fever") would eventually erase
the edge entirely at large enough jackpots. 1.3 is a middle-of-the-road
guess.

## Running it yourself

```bash
pip install -r requirements.txt
python3 scripts/run_simulation.py            # full run: ~3 min, millions of draws
python3 scripts/run_simulation.py --quick    # smoke test: a few seconds
python3 tests/test_odds.py                   # sanity check the combinatorics
```

Output lands in `results/`: one CSV per experiment (A–E above), three PNG
charts, and `summary.md` with the full per-game tables. The run already
committed to this repo used the full (non-`--quick`) settings.

## Caveats, honestly stated

- **Dollar amounts for pari-mutuel tiers aren't modeled** (match-5,
  match-6, etc. below the jackpot) because they genuinely have no fixed
  value — they depend on that specific draw's ticket sales. The
  fixed-prize tiers ($5–$500-ish) and the jackpot-tier scenarios
  (illustrative jackpot amounts) are the only dollar figures used;
  everything else is odds/probability only.
- **The population/bias model in §B is a model, not a measurement.**
  Lottery corporations don't publish how many tickets are sold per draw
  broken out by quick-pick vs. self-selected, or how self-selected
  numbers are distributed. The 12%-calendar-restricted assumption is a
  deliberately conservative placeholder based on widely-reported
  birthday-clustering behaviour (documented in other lotteries' player
  data internationally) — treat the *direction* of the result (spread
  numbers reduce sharing risk) as solid, and the exact *magnitude* as
  illustrative.
- **The rollover-dynamics model in §E is likewise a model.** The
  jackpot-growth-per-draw, the cap, and above all the sales-elasticity
  exponent are assumptions, not data pulled from operator disclosures.
  Treat the *direction* (chasing large jackpots modestly improves return
  per dollar, with diminishing returns) as the takeaway, and the exact
  cents-on-the-dollar figures as illustrative.
- **This is not investment advice.** All three games have deeply negative
  expected value per dollar under every strategy tested. The simulator is
  for understanding the math, not for finding a way to beat it — there
  isn't one.
