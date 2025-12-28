from typing import List, Optional
import os
import pandas as pd

from data import download_universe
from walkforward import run_walkforward_for_ticker
from plotting import plot_aggregate_returns, plot_regime_performance


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def run_aggregate(universe: List[str], start: str = "2012-01-01", execution: str = "close", fee_bps: float = 1.0, slippage_bps: float = 0.0, compute_regimes: bool = True) -> str:
    # Run walk-forward for each ticker, save CSVs and figures, return results folder
    outdir = "results"
    ensure_dir(outdir)
    figures = os.path.join(outdir, "figures")
    ensure_dir(figures)

    all_summaries = []
    all_regimes = []

    data = download_universe(universe, start=start)
    for ticker, df in data.items():
        try:
            if compute_regimes:
                summary, regimes = run_walkforward_for_ticker(df, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps, compute_regimes=True)
                summary["ticker"] = ticker
                regimes["ticker"] = ticker
                summary.to_csv(os.path.join(outdir, f"summary_{ticker}_{execution}.csv"), index=False)
                regimes.to_csv(os.path.join(outdir, f"regimes_{ticker}_{execution}.csv"), index=False)
                try:
                    plot_regime_performance(regimes, ticker=ticker, execution=execution, outdir=figures)
                except Exception:
                    pass
                all_summaries.append(summary)
                all_regimes.append(regimes)
            else:
                summary = run_walkforward_for_ticker(df, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps, compute_regimes=False)
                summary["ticker"] = ticker
                summary.to_csv(os.path.join(outdir, f"summary_{ticker}_{execution}.csv"), index=False)
                all_summaries.append(summary)
        except Exception as e:
            print(f"{ticker} failed: {e}")

    if len(all_summaries) == 0:
        raise RuntimeError("No summaries produced")

    summary_df = pd.concat(all_summaries, ignore_index=True)
    summary_df.to_csv(os.path.join(outdir, f"summary_all_{execution}.csv"), index=False)
    try:
        plot_aggregate_returns(summary_df, outdir=figures)
    except Exception:
        pass
    if compute_regimes and len(all_regimes) > 0:
        regimes_df = pd.concat(all_regimes, ignore_index=True)
        regimes_df.to_csv(os.path.join(outdir, f"regimes_all_{execution}.csv"), index=False)
    return outdir


if __name__ == "__main__":
    uni = ["SPY", "QQQ", "IWM", "TLT", "GLD"]
    run_aggregate(uni, execution="close", fee_bps=2.0, slippage_bps=0.5, compute_regimes=True)
from typing import List, Optional
import os
import pandas as pd

from data import download_universe
from walkforward import run_walkforward_for_ticker
from plotting import plot_aggregate_returns, plot_regime_performance


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def run_aggregate(universe: List[str], start: str = "2012-01-01", execution: str = "close", fee_bps: float = 1.0, slippage_bps: float = 0.0, compute_regimes: bool = True) -> str:
    """Run walk-forward for each ticker in universe, aggregate results, save CSVs and plots.

    Returns path to folder with results.
    """
    outdir = "results"
    ensure_dir(outdir)
    figures = os.path.join(outdir, "figures")
    ensure_dir(figures)

    all_summaries = []
    all_regimes = []

    data = download_universe(universe, start=start)
    for ticker, df in data.items():
        try:
            if compute_regimes:
                summary, regimes = run_walkforward_for_ticker(df, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps, compute_regimes=True)
                # attach ticker
                summary["ticker"] = ticker
                regimes["ticker"] = ticker
                # save per-ticker files
                summary.to_csv(os.path.join(outdir, f"summary_{ticker}_{execution}.csv"), index=False)
                regimes.to_csv(os.path.join(outdir, f"regimes_{ticker}_{execution}.csv"), index=False)
                # plot per-ticker regime figure
                try:
                    plot_regime_performance(regimes, ticker=ticker, execution=execution, outdir=figures)
                except Exception:
                    pass
                all_summaries.append(summary)
                all_regimes.append(regimes)
            else:
                summary = run_walkforward_for_ticker(df, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps, compute_regimes=False)
                summary["ticker"] = ticker
                summary.to_csv(os.path.join(outdir, f"summary_{ticker}_{execution}.csv"), index=False)
                all_summaries.append(summary)
        except Exception as e:
            print(f"{ticker} failed: {e}")

    if len(all_summaries) == 0:
        raise RuntimeError("No summaries produced")

    summary_df = pd.concat(all_summaries, ignore_index=True)
    summary_df.to_csv(os.path.join(outdir, f"summary_all_{execution}.csv"), index=False)

    # plot aggregate
    try:
        plot_aggregate_returns(summary_df, outdir=figures)
    except Exception:
        pass

    if compute_regimes and len(all_regimes) > 0:
        regimes_df = pd.concat(all_regimes, ignore_index=True)
        regimes_df.to_csv(os.path.join(outdir, f"regimes_all_{execution}.csv"), index=False)

    return outdir


if __name__ == "__main__":
    # simple runner for default universe
    uni = ["SPY", "QQQ", "IWM", "TLT", "GLD"]
    run_aggregate(uni, execution="close", fee_bps=2.0, slippage_bps=0.5, compute_regimes=True)
