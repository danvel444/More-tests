"""
Run the full strategy comparison across all three games and write results
to results/: one CSV per experiment, two PNG charts, and results/summary.md
containing the headline numbers.

Usage:
    python3 scripts/run_simulation.py [--quick]

--quick uses smaller sample sizes for a fast smoke-test run (~seconds
instead of ~1-2 minutes).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from lottery.games import ALL_GAMES
from lottery.odds import odds_table
from lottery.simulate import (
    fairness_test, jackpot_sharing_test, wheel_test, ticket_count_scaling,
    rollover_chase_test,
)

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"

# Illustrative assumptions for the jackpot-sharing model -- see
# lottery/simulate.py:expected_co_winners docstring. Adjust freely.
PLAYER_ASSUMPTIONS = {
    "649":   {"m_other_players": 6_000_000,  "f_calendar": 0.12},
    "max":   {"m_other_players": 10_000_000, "f_calendar": 0.12},
    "grand": {"m_other_players": 1_000_000,  "f_calendar": 0.12},
}

# Jackpot thresholds swept in the rollover-chasing experiment (E). Each
# game's lowest threshold equals its jackpot_reset, i.e. "always play";
# the others include the illustrative "typical" jackpot from games.py plus
# two larger rollover scenarios. Daily Grand is skipped -- its top prize is
# a fixed annuity, not a rolling jackpot (see games.py / simulate.py).
ROLLOVER_THRESHOLDS = {
    "649": [5_000_000, 12_000_000, 20_000_000, 30_000_000],
    "max": [10_000_000, 40_000_000, 60_000_000, 80_000_000],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    n_draws_fairness = 50_000 if args.quick else 2_000_000
    n_trials_sharing = 5_000 if args.quick else 200_000
    n_draws_wheel = 20_000 if args.quick else 300_000
    n_draws_scaling = 20_000 if args.quick else 300_000
    n_draws_rollover = 20_000 if args.quick else 1_000_000

    RESULTS_DIR.mkdir(exist_ok=True)
    summary_lines = ["# Lottery Strategy Simulation -- Results\n"]

    all_fairness = []
    all_sharing = []
    all_wheel = []
    all_scaling = []
    all_rollover = []

    for game in ALL_GAMES.values():
        print(f"=== {game.display_name} ===")
        summary_lines.append(f"\n## {game.display_name}\n")

        # --- odds table -----------------------------------------------
        odt = pd.DataFrame(odds_table(game))
        summary_lines.append("### Official odds by tier\n")
        summary_lines.append(odt.to_markdown(index=False, floatfmt=",.1f"))
        summary_lines.append("")

        # --- A. fairness -------------------------------------------------
        print("  running fairness test...")
        f = fairness_test(game, n_draws=n_draws_fairness, n_fixed_players=25, seed=42)
        f["game"] = game.key
        all_fairness.append(f)
        pivot = (f.groupby(["strategy", "tier"])["empirical_prob"].mean()
                 .unstack("strategy"))
        theory = f.drop_duplicates("tier").set_index("tier")["theoretical_prob"]
        pivot["theoretical"] = theory
        summary_lines.append("### A. Fixed numbers vs. Quick Pick -- empirical hit rate per tier\n")
        summary_lines.append(f"(n = {n_draws_fairness:,} simulated draws, 25 independent fixed players averaged)\n")
        summary_lines.append(pivot.to_markdown(floatfmt=",.6f"))
        summary_lines.append("")

        # --- B. jackpot sharing -------------------------------------------
        print("  running jackpot-sharing test...")
        pa = PLAYER_ASSUMPTIONS[game.key]
        sh = jackpot_sharing_test(game, m_other_players=pa["m_other_players"],
                                   f_calendar=pa["f_calendar"],
                                   jackpot=game.jackpot_typical,
                                   n_trials=n_trials_sharing, seed=42)
        sh["game"] = game.key
        all_sharing.append(sh)
        summary_lines.append(
            f"### B. Jackpot-sharing risk (assuming ~{pa['m_other_players']:,} other tickets in play, "
            f"{pa['f_calendar']*100:.0f}% of all players restricted to numbers 1-31, "
            f"illustrative jackpot ${game.jackpot_typical:,.0f})\n")
        summary_lines.append(sh.to_markdown(index=False, floatfmt=",.3f"))
        summary_lines.append("")

        # --- C. wheel vs random (skip for tiny pools where wheel is huge) --
        wheel_pool = min(game.pool_size, game.pick_count + 3)
        print(f"  running wheel test (pool={wheel_pool})...")
        w = wheel_test(game, wheel_pool_size=wheel_pool, n_draws=n_draws_wheel, seed=42)
        w["game"] = game.key
        all_wheel.append(w)
        summary_lines.append("### C. Wheeling system vs. same number of random lines\n")
        summary_lines.append(w.to_markdown(index=False, floatfmt=",.5f"))
        summary_lines.append("")

        # --- D. ticket count scaling ---------------------------------------
        print("  running ticket-count scaling test...")
        t = ticket_count_scaling(game, [1, 5, 20, 50], n_draws=n_draws_scaling, seed=42)
        t["game"] = game.key
        all_scaling.append(t)
        summary_lines.append("### D. Return per dollar vs. number of lines played per draw\n")
        summary_lines.append(t.to_markdown(index=False, floatfmt=",.5f"))
        summary_lines.append("")

        # --- E. rollover chasing (skip games with no rolling jackpot) ------
        if game.key in ROLLOVER_THRESHOLDS:
            print("  running rollover-chasing test...")
            r = rollover_chase_test(game, ROLLOVER_THRESHOLDS[game.key],
                                     n_draws=n_draws_rollover, f_calendar=0.12, seed=42)
            r["game"] = game.key
            all_rollover.append(r)
            summary_lines.append(
                "### E. Rollover chasing -- only play when the jackpot clears a threshold\n")
            summary_lines.append(
                f"(simulated {n_draws_rollover:,}-draw jackpot trajectory; "
                f"reset ${game.jackpot_reset:,.0f}, cap "
                f"{'$' + format(game.jackpot_cap, ',.0f') if game.jackpot_cap else 'none'}, "
                f"+${game.jackpot_increment:,.0f}/unwon draw, sales scale as "
                f"(J/reset)^{game.sales_elasticity} off a base of {game.sales_base:,} tickets)\n")
            summary_lines.append(r.to_markdown(index=False, floatfmt=",.4f"))
            summary_lines.append("")

    fairness_df = pd.concat(all_fairness, ignore_index=True)
    sharing_df = pd.concat(all_sharing, ignore_index=True)
    wheel_df = pd.concat(all_wheel, ignore_index=True)
    scaling_df = pd.concat(all_scaling, ignore_index=True)
    rollover_df = pd.concat(all_rollover, ignore_index=True)

    fairness_df.to_csv(RESULTS_DIR / "fairness_results.csv", index=False)
    sharing_df.to_csv(RESULTS_DIR / "sharing_results.csv", index=False)
    wheel_df.to_csv(RESULTS_DIR / "wheel_results.csv", index=False)
    scaling_df.to_csv(RESULTS_DIR / "scaling_results.csv", index=False)
    rollover_df.to_csv(RESULTS_DIR / "rollover_results.csv", index=False)

    # --- charts -------------------------------------------------------
    make_fairness_chart(fairness_df)
    make_sharing_chart(sharing_df)
    make_rollover_chart(rollover_df)

    (RESULTS_DIR / "summary.md").write_text("\n".join(summary_lines))
    print(f"\nDone. Results written to {RESULTS_DIR}/")


def make_fairness_chart(fairness_df: pd.DataFrame):
    games = fairness_df["game"].unique()
    fig, axes = plt.subplots(1, len(games), figsize=(16, 6.5))
    for ax, gkey in zip(axes, games):
        sub = fairness_df[fairness_df["game"] == gkey]
        pivot = sub.groupby(["tier", "strategy"])["empirical_prob"].mean().unstack("strategy")
        theory = sub.drop_duplicates("tier").set_index("tier")["theoretical_prob"]
        pivot = pivot.loc[theory.sort_values(ascending=False).index]
        pivot.plot(kind="bar", ax=ax, width=0.8, legend=False)
        ax.scatter(range(len(pivot)), theory.loc[pivot.index], color="black", zorder=5,
                   marker="_", s=200, label="theoretical")
        ax.set_yscale("log")
        ax.set_title(gkey)
        ax.set_ylabel("hit probability (log scale)")
        ax.tick_params(axis="x", rotation=75, labelsize=8)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0), fontsize=9)
    fig.suptitle("Fixed Numbers vs Quick Pick: empirical hit rate per tier (bars should overlap the theoretical line)",
                 y=1.08)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "fairness_chart.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def make_sharing_chart(sharing_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    games = sharing_df["game"].unique()
    width = 0.35
    import numpy as np
    x = np.arange(len(games))
    popular = sharing_df[sharing_df["scenario"].str.contains("Popular")]["mean_payout_sim"].values
    spread = sharing_df[sharing_df["scenario"].str.contains("Quick pick")]["mean_payout_sim"].values
    ax.bar(x - width/2, popular, width, label="Popular / calendar numbers (≤ 31)")
    ax.bar(x + width/2, spread, width, label="Quick pick / spread numbers")
    ax.set_xticks(x)
    ax.set_xticklabels(games)
    ax.set_ylabel("Expected jackpot payout ($), after splitting")
    ax.set_title("Expected jackpot payout by number-choice pattern")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "sharing_chart.png", dpi=140)
    plt.close(fig)


def make_rollover_chart(rollover_df: pd.DataFrame):
    games = rollover_df["game"].unique()
    fig, axes = plt.subplots(1, len(games), figsize=(11, 4.5))
    if len(games) == 1:
        axes = [axes]
    for ax, gkey in zip(axes, games):
        sub = rollover_df[rollover_df["game"] == gkey].sort_values("threshold")
        ax.plot(sub["mean_jackpot_when_played"] / 1e6, sub["return_per_dollar"] * 100,
                marker="o")
        for _, row in sub.iterrows():
            ax.annotate(f"≥${row['threshold']/1e6:.0f}M\n({row['fraction_of_draws_played']*100:.1f}% of draws)",
                        (row["mean_jackpot_when_played"] / 1e6, row["return_per_dollar"] * 100),
                        textcoords="offset points", xytext=(6, 6), fontsize=7)
        ax.set_xlabel("mean jackpot when you play ($M)")
        ax.set_ylabel("return per dollar (cents on the $)")
        ax.set_title(gkey)
        ax.grid(alpha=0.3)
    fig.suptitle("Rollover chasing: return per dollar vs. minimum jackpot played")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "rollover_chart.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
