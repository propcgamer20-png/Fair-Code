"""Renders the paper figures - Layer 2 of the benchmark harness.

Reads results_fairness.csv (written by faircode.benchmark) from disk and
renders one 300-dpi PNG per audit into <results_dir>/figures/: the chosen
fairness metric's point estimate (averaged across the three model families)
across the five mitigation strategies. This module never re-runs a model -
it only visualizes what benchmark.py already computed, so re-plotting with a
different metric doesn't require re-running the harness.

Requires matplotlib, the optional 'benchmark' extra
(`pip install faircode[benchmark]`).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .strategies import STRATEGIES

FIGURE_DPI = 300


_BAR_COLORS = ("#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860")


def plot_strategy_comparison(fairness_df: pd.DataFrame, audit: str, out_path,
                             metric: str = "demographic_parity_diff"):
    """Bar chart of `metric`'s point estimate across the five mitigation
    strategies (averaged across model families) for one audit.

    For an audit that declares more than one protected attribute, the value
    is broken out into one bar per protected attribute within each strategy
    group, rather than averaged into a single bar - averaging across
    different protected attributes blends genuinely different (often
    oppositely-signed) fairness gaps into one number that represents none of
    them (#525). A single-attribute audit renders one bar per strategy as
    before.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    subset = fairness_df[(fairness_df["audit"] == audit) & (fairness_df["metric"] == metric)]
    if subset.empty:
        raise ValueError(f"no rows for audit={audit!r} metric={metric!r}")

    has_pa = "protected_attribute" in subset.columns
    attrs = sorted(subset["protected_attribute"].dropna().unique()) if has_pa else []

    fig, ax = plt.subplots(figsize=(8, 4.5))

    if len(attrs) > 1:
        x = np.arange(len(STRATEGIES))
        width = 0.8 / len(attrs)
        for i, attr in enumerate(attrs):
            per_strategy = (subset[subset["protected_attribute"] == attr]
                            .groupby("strategy")["value"].mean().reindex(STRATEGIES))
            offset = (i - (len(attrs) - 1) / 2) * width
            ax.bar(x + offset, per_strategy.to_numpy(), width,
                   label=str(attr), color=_BAR_COLORS[i % len(_BAR_COLORS)])
        ax.set_xticks(x)
        ax.set_xticklabels(STRATEGIES)
        ax.legend(title="protected attribute")
        title = (f"{audit}: {metric.replace('_', ' ')} by protected attribute "
                 f"across mitigation strategies")
    else:
        grouped = subset.groupby("strategy")["value"].mean().reindex(STRATEGIES)
        ax.bar(grouped.index, grouped.to_numpy(), color=_BAR_COLORS[0])
        title = f"{audit}: {metric.replace('_', ' ')} across mitigation strategies"

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel(metric.replace("_", " "))
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIGURE_DPI)
    plt.close(fig)


def generate_figures(results_dir, figures_dir=None, metric: str = "demographic_parity_diff"):
    """Read results_fairness.csv from results_dir and write one
    <audit>_strategies.png per audit into figures_dir (default:
    <results_dir>/figures/)."""
    results_dir = Path(results_dir)
    figures_dir = Path(figures_dir) if figures_dir else results_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    fairness_df = pd.read_csv(results_dir / "results_fairness.csv")
    for audit in fairness_df["audit"].unique():
        plot_strategy_comparison(
            fairness_df, audit, figures_dir / f"{audit}_strategies.png", metric=metric)
    return figures_dir


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="faircode-figures",
        description="Render paper figures from a benchmark results directory.")
    parser.add_argument("results_dir", nargs="?", default="results",
                       help="directory containing results_fairness.csv (default: results)")
    parser.add_argument("--metric", default="demographic_parity_diff",
                       help="fairness metric to plot (default: demographic_parity_diff)")
    args = parser.parse_args(argv)

    figures_dir = generate_figures(args.results_dir, metric=args.metric)
    print(f"Figures written to {figures_dir}/")


if __name__ == "__main__":
    main()
