# farkle_sim — Farkle strategy Monte Carlo simulator

A dependency-free Python toolkit for answering "what's the optimal Farkle
strategy?" with actual numbers instead of gut feel: an exact scoring
engine, exact roll probabilities (full enumeration, not textbook
approximations), several bank-vs-reroll strategies, and a Monte Carlo
tournament runner.

## Rules implemented

Standard six-dice Farkle:

- Single **1** = 100 pts, single **5** = 50 pts
- Three of a kind: three 1s = 1000, three of face *N* = *N* × 100
- Four/five/six of a kind: double the three-of-a-kind value per extra die
  (4-kind = 2×, 5-kind = 4×, 6-kind = 8× the base triple)
- Straight (1-2-3-4-5-6 in one roll) = 1500
- Three pairs (in one roll) = 1500
- Roll with **no** scoring dice = Farkle: the entire turn's banked-in-hand
  score is lost and the turn ends immediately
- **Hot dice**: if every die in a roll scores, re-roll all six with your
  turn score intact
- **Minimum entry**: you must score ≥300 in a single turn before those
  points (or any future turn's points) count toward your total; below
  that you're forced to keep rolling rather than bank
- **Target score / final round**: first player to reach 10,000 total
  triggers one final turn for everyone else, then the highest total wins

All of this is configurable (`--target`, `--min-entry`) via the CLI.

## Layout

```
farkle_sim/
  scoring.py        exact roll scorer (max-value decomposition of a roll)
  probabilities.py  exact Farkle/hit probabilities via full 6^n enumeration
  strategies.py      bank-vs-reroll decision strategies
  game.py            single-turn and full multiplayer game engine
  simulate.py        Monte Carlo tournament runner
  cli.py             command-line entry point
tests/               unit tests (32 tests, run with `python3 -m unittest discover -s tests`)
```

## Usage

```bash
# exact per-roll probabilities + EV-optimal breakeven thresholds
python3 -m farkle_sim.cli probabilities

# compare a family of fixed thresholds + the EV-optimal strategy
python3 -m farkle_sim.cli sweep --games 20000

# a fixed roster of representative strategies, 8-player free-for-all
python3 -m farkle_sim.cli tournament --games 20000

# head-to-head duel (spec is an int threshold, "ev", or "catch_up")
python3 -m farkle_sim.cli duel --a ev --b 300 --games 20000
```

## The question: go big, or bank small points?

**Neither, as a blanket rule — the right answer depends entirely on how
many dice you have left, and it swings hard.** That's the core finding
here, and it's provable from exact roll math before a single simulated
game is even played.

### The exact odds, dice remaining → risk

| dice remaining | P(Farkle) | E[score \| you score] |
|---:|---:|---:|
| 1 | 66.7% | 75 |
| 2 | 44.4% | 90 |
| 3 | 27.8% | 120 |
| 4 | 15.7% | 170 |
| 5 | 7.7% | 245 |
| 6 (fresh turn / hot dice) | 2.3% | 420 |

Rolling one die left is a coin-flip-and-then-some against you (2 in 3
busts). Rolling a fresh six is nearly safe (~2% bust). That's a
30x swing in risk depending only on dice count — strategies that ignore
it and chase a single flat point target are leaving money on the table.

### The EV-optimal breakeven

From those exact odds you can derive, per dice-remaining count, the turn
score at which rolling again and banking now have equal expected value
(below it, keep rolling; at/above it, bank):

| dice remaining | breakeven turn score |
|---:|---:|
| 1 | ~38 |
| 2 | ~112 |
| 3 | ~312 |
| 4 | ~912 |
| 5 | ~2,926 |
| 6 (fresh/hot dice) | ~17,742 |

Read that as the actual strategy: **with lots of dice left, keep rolling
almost no matter what you've banked this turn — the risk is tiny and the
upside is large. With one or two dice left, bank almost anything, because
you're a coin-flip (or worse) from losing it all.** A flat "always stop at
300" or "always go for 1000" rule is exactly wrong in one of those two
regimes every time you use it.

### What the simulations show

An `ExpectedValueStrategy` implementing that dice-count-aware breakeven
rule beats every fixed-threshold strategy tested, decisively:

**8-player free-for-all, 20,000 games** (win rate = share of games won):

| strategy | win % | avg score | bust % |
|---|---:|---:|---:|
| **ev_optimal** | **28.7%** (should be ~12.5% if all were equal) | 8,654 | 17.5% |
| threshold(300) | 12.6% | 7,832 | 19.5% |
| catch_up (score-aware) | 12.4% | 7,653 | 31.7% |
| threshold(200) | 11.6% | 7,727 | 8.1% |
| threshold(500) | 9.7% | 7,081 | 49.4% |
| threshold(800) | 9.2% | 6,544 | 65.8% |
| threshold(1500) | 3.1% | 4,503 | 84.2% |

**Head-to-head, 20,000 games each:**

| matchup | result |
|---|---|
| ev_optimal vs threshold(300) | **64.2% vs 35.8%** |
| ev_optimal vs catch_up | **65.0% vs 35.0%** |
| threshold(300) vs threshold(500) | **61.9% vs 38.1%** |

Two clear, consistent patterns across every run:

1. **A fixed "bank at N" number is always a compromise.** Too low
   (150–300) and you're leaving huge amounts of expected value on the
   table on 5-and-6-dice rolls, where busting is rare. Too high
   (800–2000) and your bust rate explodes (66–91%!) because you keep
   pushing your luck even down to 1–2 dice, where the odds have flipped
   against you.
2. **Going big only pays off early in the dice sequence.** With 4+ dice
   left, keep pushing — the math strongly favors it (bust chance ≤15.7%).
   With 1–2 dice left, take the small points and bank — the math
   strongly favors that too (44–67% bust chance). The winning strategy
   isn't "aggressive" or "conservative," it's *adaptive to dice count*.

The threshold-only strategies that do best (200–300) do so because they
implicitly stop before too many low-dice, high-risk rolls happen — but
they still both underreact (bank too early on great early rolls) and
overreact (occasionally still push a 4th or 5th roll on 2 dice) relative
to the dice-aware rule. `threshold(300)+floor(1)` — bank at 300 *or*
whenever only 1 die is left, whichever comes first — closes part of that
gap but still trails `ev_optimal` because it doesn't scale the bailout
point with 2, 3, or 4 dice remaining, only 1.

### Practical takeaway

If you want one sentence: **don't pick a target score at all — decide
each roll based on how many dice you'd have to re-roll.** Keep rolling
almost automatically with 4, 5, or 6 dice in hand; get nervous and bank at
2; bank on sight at 1, unless you're desperate and behind late in the
game. That single rule outperformed every fixed-number strategy tested by
a wide margin.

## Extending this

- `strategies.py` has a clean `Strategy.decide(ctx) -> bool` interface —
  new strategies (e.g. Monte-Carlo-lookahead instead of 1-ply EV, or
  ruleset variants like requiring 500 to get on the board) drop in
  easily.
- `probabilities.py`'s enumeration is exact for *this* ruleset; if you
  add/remove scoring combinations in `scoring.py`, re-run
  `python3 -m farkle_sim.probabilities` and the breakevens update
  automatically — nothing is hardcoded.
