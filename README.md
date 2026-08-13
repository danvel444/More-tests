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

## Deep dive: does "stop at 2 dice" actually work? (1,000,000-game runs)

`scripts/stop_at_k_dice.py` and `scripts/duel_mp.py` isolate this exact
question: strategies that bank the instant `dice_remaining <= K` and
otherwise *never* bank on score alone (K = 1, 2, 3), run at 1,000,000
games apiece (multiprocessed across 4 workers, ~2-5 min per run).

**5-way free-for-all, 1,000,000 games:**

| strategy | win % | avg score | bust % |
|---|---:|---:|---:|
| ev_optimal (dice + score aware) | **29.5%** | 8,575 | 17.5% |
| stop_at_3_dice | 24.7% | 8,311 | 9.4% |
| stop_at_2_dice | 24.0% | 8,191 | 21.3% |
| threshold(300) | 13.2% | 7,737 | 19.6% |
| stop_at_1_die | 8.5% | 6,435 | 47.1% |

**Head-to-head duels, 1,000,000 games each:**

| matchup | result |
|---|---|
| stop_at_2_dice vs threshold(300) | **57.3% vs 42.7%** |
| stop_at_3_dice vs stop_at_2_dice | **51.3% vs 48.7%** |
| ev_optimal vs stop_at_2_dice | **55.5% vs 44.5%** |
| ev_optimal vs stop_at_3_dice | **53.8% vs 46.2%** |

**So: yes, "stop at 2 dice left" is a good rule** — it beats a flat
`threshold(300)` 57–43 and crushes "ride it to 1 die." But it's not quite
the ceiling: "stop at 3 dice left" edges it out (51.3–48.7), and the full
dice-*and*-score-aware rule beats both by a wider margin (~54–55%).

**Why 3 beats 2, and why both lose to the adaptive rule:** the earlier
breakeven table said the 2-dice bank point is ~112 — but the *minimum*
turn score you can possibly have when you're down to 2 dice remaining is
200 (you had to use 4 dice to get there, and the cheapest die value in
this ruleset is a lone 5 at 50 points, so 4 × 50 = 200 is the floor).
200 already clears the ~112 breakeven, which means **a properly adaptive
player bans at 2 dice almost automatically anyway** — "stop at 2" isn't
so much a separate rule as a natural consequence of the real one.

The reason `stop_at_2_dice` underperforms `stop_at_3_dice` is that it's
*blind to score*: it pushes through the 3-dice checkpoint unconditionally,
even on the (not-rare) turns where a hot-dice streak has already built a
turn score of 1,000+ sitting at 3 dice remaining — a spot where the math
says bank (breakeven at 3 dice is ~312), not gamble a 27.8% bust chance
against it. `stop_at_3_dice` never makes that mistake because it always
bails at 3; but it also always leaves value on the table on the (more
common) turns where the score sitting at 3 dice is still small enough
that pushing on was actually worth it. `ev_optimal` is the only one of
the three that gets both cases right, which is why it beats both pure
floors.

**Practical version of the rule, in order of importance:**
1. Always bank once you're down to 2 dice, no exceptions — the math
   guarantees you've already cleared the bar.
2. At 3 dice, bank unless your turn score is still small (roughly
   under ~300) — if a hot-dice run has already pumped you well past
   that, stop pushing your luck there too, don't wait for 2 dice.
3. With 4+ dice in hand, keep rolling almost regardless of score — that
   territory is safe enough (≤15.7% bust) that the blind
   `stop_at_3`/`stop_at_2` floors did essentially as well as the
   fully-adaptive rule there; the adaptive rule's edge comes almost
   entirely from getting the 3-dice judgment call right.

## Self-play control check

All the win-rate numbers above come from *mixed* fields (different
strategies sharing a table), which raises a fair question: is a
strategy's win rate a genuine skill edge, or an artifact of the specific
opponents/shuffling in that run? `scripts/self_play.py` seats N clones of
the *same* strategy together — since everyone at the table is identical,
each clone's win rate should land statistically on 1/N with no structural
advantage for any seat, and any real bias in the engine (turn order,
shuffling, the final-round trigger) would show up as skew here.

**5 clones each, 20,000 games:**

| strategy | win% across the 5 identical seats | intrinsic avg score | intrinsic bust% |
|---|---|---:|---:|
| ev_optimal | 19.6–20.6% | 8,021 | 17.5% |
| stop_at_3_dice | 19.5–20.6% | 8,019 | 9.4% |
| stop_at_2_dice | 19.8–20.1% | 7,920 | 21.3% |
| catch_up | 19.6–20.3% | 8,254 | 29.9% |
| threshold(300) | 19.3–21.2% | 8,369 | 19.6% |

Every strategy landed within noise of 20.00% (biggest spread under 2
points on 20,000 games) — confirms the engine has no seat/turn-order
bias. This is a control, not evidence of skill (self-play is symmetric by
construction and can't produce a skill gap); the actual evidence that
`ev_optimal` beats `stop_at_2_dice`/`stop_at_3_dice` is the pairwise
duels in the section above, and this run is what says those results
weren't a simulator artifact.

Note the "intrinsic" avg scores here run a little lower than the same
strategies' avg scores in the earlier mixed fields (e.g. `ev_optimal`:
8,021 self-play vs 8,575 in the 5-way mixed run) — a table of equally
fast/aggressive players races to the target quicker than a table
containing slow, high-bust strategies that drag the game out.

## Extending this

- `strategies.py` has a clean `Strategy.decide(ctx) -> bool` interface —
  new strategies (e.g. Monte-Carlo-lookahead instead of 1-ply EV, or
  ruleset variants like requiring 500 to get on the board) drop in
  easily.
- `probabilities.py`'s enumeration is exact for *this* ruleset; if you
  add/remove scoring combinations in `scoring.py`, re-run
  `python3 -m farkle_sim.probabilities` and the breakevens update
  automatically — nothing is hardcoded.
