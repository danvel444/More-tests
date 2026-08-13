"""Command-line interface for the Farkle strategy simulator.

Examples
--------
    python -m farkle_sim.cli probabilities
    python -m farkle_sim.cli sweep --games 20000
    python -m farkle_sim.cli tournament --games 20000
    python -m farkle_sim.cli duel --a 300 --b ev --games 20000
"""

from __future__ import annotations

import argparse

from .game import DEFAULT_MIN_ENTRY, DEFAULT_TARGET_SCORE
from .probabilities import all_dice_stats
from .simulate import print_leaderboard, run_tournament
from .strategies import (
    CatchUpStrategy,
    ExpectedValueStrategy,
    ThresholdStrategy,
    ThresholdWithFloorStrategy,
)


def cmd_probabilities(args: argparse.Namespace) -> None:
    print(f"{'dice':>4} {'P(farkle)':>10} {'E[score]':>10} {'E[score|hit]':>13} {'P(hot dice)':>12}")
    for s in all_dice_stats():
        print(
            f"{s.dice:>4} {s.farkle_probability:>10.4f} {s.expected_score:>10.1f} "
            f"{s.expected_score_given_hit:>13.1f} {s.hot_dice_probability:>12.4f}"
        )
    print()
    ev = ExpectedValueStrategy()
    print("EV-breakeven turn score by dice remaining (roll again below this, bank at/above):")
    for n, v in sorted(ev.breakeven_table().items()):
        print(f"  {n} dice remaining -> breakeven turn score ~= {v:,.0f}")


def cmd_sweep(args: argparse.Namespace) -> None:
    thresholds = args.thresholds or [150, 200, 250, 300, 350, 400, 500, 600, 800, 1000, 1500, 2000]
    contestants = [(f"threshold({t})", ThresholdStrategy(t)) for t in thresholds]
    contestants.append(("ev_optimal", ExpectedValueStrategy()))
    contestants.append(("threshold(300)+floor(1)", ThresholdWithFloorStrategy(300, 1)))
    stats = run_tournament(
        contestants, games=args.games, target_score=args.target, min_entry=args.min_entry, seed=args.seed
    )
    print(f"Sweep over {len(contestants)} strategies, {args.games} {len(contestants)}-player games:\n")
    print(print_leaderboard(stats))


def cmd_tournament(args: argparse.Namespace) -> None:
    contestants = [
        ("threshold(200)", ThresholdStrategy(200)),
        ("threshold(300)", ThresholdStrategy(300)),
        ("threshold(500)", ThresholdStrategy(500)),
        ("threshold(800)", ThresholdStrategy(800)),
        ("threshold(1500)", ThresholdStrategy(1500)),
        ("threshold(300)+floor(1)", ThresholdWithFloorStrategy(300, 1)),
        ("ev_optimal", ExpectedValueStrategy()),
        ("catch_up", CatchUpStrategy()),
    ]
    stats = run_tournament(
        contestants, games=args.games, target_score=args.target, min_entry=args.min_entry, seed=args.seed
    )
    print(f"Tournament: {len(contestants)}-player free-for-all, {args.games} games:\n")
    print(print_leaderboard(stats))


_NAMED_STRATEGIES = {
    "ev": lambda: ExpectedValueStrategy(),
    "catch_up": lambda: CatchUpStrategy(),
}


def _resolve_strategy(spec: str):
    if spec in _NAMED_STRATEGIES:
        return _NAMED_STRATEGIES[spec]()
    return ThresholdStrategy(int(spec))


def cmd_duel(args: argparse.Namespace) -> None:
    a = _resolve_strategy(args.a)
    b = _resolve_strategy(args.b)
    stats = run_tournament(
        [(f"A:{a}", a), (f"B:{b}", b)],
        games=args.games,
        target_score=args.target,
        min_entry=args.min_entry,
        seed=args.seed,
    )
    print(f"Duel: {a} vs {b}, {args.games} games:\n")
    print(print_leaderboard(stats))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Farkle strategy Monte Carlo simulator")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("probabilities", help="print exact per-roll Farkle probabilities and EV breakevens")
    p.set_defaults(func=cmd_probabilities)

    p = sub.add_parser("sweep", help="compare a family of threshold strategies (+ EV-optimal) head to head")
    p.add_argument("--games", type=int, default=20_000)
    p.add_argument("--target", type=int, default=DEFAULT_TARGET_SCORE)
    p.add_argument("--min-entry", type=int, default=DEFAULT_MIN_ENTRY)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--thresholds", type=int, nargs="*", default=None)
    p.set_defaults(func=cmd_sweep)

    p = sub.add_parser("tournament", help="run a fixed roster of representative strategies against each other")
    p.add_argument("--games", type=int, default=20_000)
    p.add_argument("--target", type=int, default=DEFAULT_TARGET_SCORE)
    p.add_argument("--min-entry", type=int, default=DEFAULT_MIN_ENTRY)
    p.add_argument("--seed", type=int, default=None)
    p.set_defaults(func=cmd_tournament)

    p = sub.add_parser("duel", help="pit two strategies head to head (spec: an integer threshold, 'ev', or 'catch_up')")
    p.add_argument("--a", type=str, required=True)
    p.add_argument("--b", type=str, required=True)
    p.add_argument("--games", type=int, default=20_000)
    p.add_argument("--target", type=int, default=DEFAULT_TARGET_SCORE)
    p.add_argument("--min-entry", type=int, default=DEFAULT_MIN_ENTRY)
    p.add_argument("--seed", type=int, default=None)
    p.set_defaults(func=cmd_duel)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
