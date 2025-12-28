import os
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_regime_performance(regimes_df: pd.DataFrame, ticker: str = "TICK", execution: str = "close", outdir: Optional[str] = "results/figures") -> str:
    # Save a figure summarizing per-regime ann returns
    ensure_dir(outdir)
    fig_path = os.path.join(outdir, f"{ticker}_{execution}_regimes.png")
    if regimes_df is None or len(regimes_df) == 0:
        raise ValueError("regimes_df is empty; no regime data to plot")
    if "regime" not in regimes_df.columns:
        raise ValueError("regimes_df must contain a 'regime' column")
    agg = regimes_df.groupby("regime")["ann_return"].agg(["mean", "std", "count"]).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(agg["regime"].astype(str), agg["mean"], yerr=agg["std"], capsize=5)
    axes[0].set_title(f"Mean test ann return by regime ({ticker} {execution})")
    axes[0].set_xlabel("Regime (1=low vol)")
    axes[0].set_ylabel("Annualized return")
    regimes_df.boxplot(column="ann_return", by="regime", ax=axes[1])
    axes[1].set_title("Distribution of ann returns by regime (per fold)")
    axes[1].set_xlabel("Regime")
    axes[1].set_ylabel("Annualized return")
    plt.suptitle("")
    plt.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)
    return fig_path


def plot_aggregate_returns(summary_df: pd.DataFrame, outdir: Optional[str] = "results/figures") -> str:
    # Save a bar chart of mean OOS annual return per ticker
    ensure_dir(outdir)
    fig_path = os.path.join(outdir, "aggregate_oos_returns.png")
    agg = summary_df.groupby("ticker")["test_ann_return"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    agg.plot.bar(ax=ax)
    ax.set_title("Mean OOS annual return by ticker (walk-forward)")
    ax.set_ylabel("Annualized return")
    ax.set_xlabel("")
    plt.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)
    return fig_path
import os
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_regime_performance(regimes_df: pd.DataFrame, ticker: str = "TICK", execution: str = "close", outdir: Optional[str] = "results/figures") -> str:
    """Plot aggregated regime performance and save figure.

    Expects regimes_df with columns: regime, ann_return (per-fold per-regime).
    Returns path to saved figure.
    """
    ensure_dir(outdir)
    fig_path = os.path.join(outdir, f"{ticker}_{execution}_regimes.png")

    # basic aggregation: mean ann_return per regime
    if regimes_df is None or len(regimes_df) == 0:
        raise ValueError("regimes_df is empty; no regime data to plot")
    if "regime" not in regimes_df.columns:
        raise ValueError("regimes_df must contain a 'regime' column")

    agg = regimes_df.groupby("regime")["ann_return"].agg(["mean", "std", "count"]).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart of mean returns
    axes[0].bar(agg["regime"].astype(str), agg["mean"], yerr=agg["std"], capsize=5)
    axes[0].set_title(f"Mean test ann return by regime ({ticker} {execution})")
    axes[0].set_xlabel("Regime (1=low vol)")
    axes[0].set_ylabel("Annualized return")

    # Boxplot of per-fold ann_return by regime
    regimes_df.boxplot(column="ann_return", by="regime", ax=axes[1])
    axes[1].set_title("Distribution of ann returns by regime (per fold)")
    axes[1].set_xlabel("Regime")
    axes[1].set_ylabel("Annualized return")
    plt.suptitle("")
    plt.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)
    return fig_path


def plot_aggregate_returns(summary_df: pd.DataFrame, outdir: Optional[str] = "results/figures") -> str:
    """Plot mean test_ann_return per ticker from summary_df and save figure.

    Expects summary_df to have columns: ticker, test_ann_return
    """
    ensure_dir(outdir)
    fig_path = os.path.join(outdir, "aggregate_oos_returns.png")

    agg = summary_df.groupby("ticker")["test_ann_return"].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    agg.plot.bar(ax=ax)
    ax.set_title("Mean OOS annual return by ticker (walk-forward)")
    ax.set_ylabel("Annualized return")
    ax.set_xlabel("")
    plt.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)
    return fig_path
