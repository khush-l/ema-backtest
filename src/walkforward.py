from typing import List, Tuple
import pandas as pd
import numpy as np

from signals import make_signals
from backtest import backtest_close, backtest_open
from metrics import perf_stats
import regimes as regimes_mod


def _year_offset(dt: pd.Timestamp, years: int) -> pd.Timestamp:
    try:
        return dt.replace(year=dt.year + years)
    except Exception:
        return dt + pd.DateOffset(years=years)


def rolling_splits(dates: pd.DatetimeIndex, train_years: int = 7, test_years: int = 3) -> List[Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    # Return list of (train_start, train_end, test_start, test_end) folds
    if not isinstance(dates, pd.DatetimeIndex):
        dates = pd.to_datetime(dates)
    start = dates.min()
    end = dates.max()
    folds = []
    train_start = start
    train_end = _year_offset(train_start, train_years) - pd.Timedelta(days=1)
    while True:
        test_start = train_end + pd.Timedelta(days=1)
        test_end = _year_offset(test_start, test_years) - pd.Timedelta(days=1)
        if test_end > end:
            break
        folds.append((train_start, train_end, test_start, test_end))
        train_start = _year_offset(train_start, test_years)
        train_end = _year_offset(train_start, train_years) - pd.Timedelta(days=1)
    return folds


def grid_search_train(df: pd.DataFrame, train_start: pd.Timestamp, train_end: pd.Timestamp, grid: List[Tuple[int, int]], execution: str = "close", fee_bps: float = 1.0, slippage_bps: float = 0.0) -> Tuple[int, int, dict]:
    # Grid search on train window; returns best (fast, slow, stats) by ann return
    best = None
    best_metric = -np.inf
    train_df = df.loc[train_start:train_end]
    for fast, slow in grid:
        if slow <= fast:
            continue
        sig = make_signals(train_df, fast=fast, slow=slow)
        if execution == "close":
            bt = backtest_close(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
        else:
            bt = backtest_open(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
        stats = perf_stats(bt["strat_ret"]) if "strat_ret" in bt else perf_stats(bt["ret"])
        ann = float(stats.get("ann_return", -np.inf) or -np.inf)
        if ann > best_metric:
            best_metric = ann
            best = (fast, slow, stats)
    if best is None:
        raise ValueError("No valid parameter combination found in grid")
    return best


def evaluate_params(df: pd.DataFrame, fast: int, slow: int, test_start: pd.Timestamp, test_end: pd.Timestamp, execution: str = "close", fee_bps: float = 1.0, slippage_bps: float = 0.0) -> dict:
    # Evaluate chosen params on test window and return stats
    test_df = df.loc[test_start:test_end]
    sig = make_signals(test_df, fast=fast, slow=slow)
    if execution == "close":
        bt = backtest_close(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
    else:
        bt = backtest_open(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
    stats = perf_stats(bt["strat_ret"]) if "strat_ret" in bt else perf_stats(bt["ret"])
    return stats


def run_walkforward_for_ticker(df: pd.DataFrame, grid: List[Tuple[int, int]] = None, train_years: int = 7, test_years: int = 3, fee_bps: float = 1.0, slippage_bps: float = 0.0, execution: str = "close", compute_regimes: bool = False, vol_window: int = 21, vol_q: int = 4):
    # Run rolling walk-forward on one ticker. Returns summary or (summary, regimes_df).
    if grid is None:
        grid = [(f, s) for f in range(5, 31, 5) for s in range(10, 61, 5)]
    idx = pd.to_datetime(df.index)
    folds = rolling_splits(idx, train_years=train_years, test_years=test_years)
    rows = []
    regimes_rows = []
    for train_start, train_end, test_start, test_end in folds:
        try:
            best_fast, best_slow, train_stats = grid_search_train(df, train_start, train_end, grid, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps)
            test_stats = evaluate_params(df, best_fast, best_slow, test_start, test_end, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps)
            rows.append({
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "best_fast": int(best_fast),
                "best_slow": int(best_slow),
                "train_ann_return": float(train_stats.get("ann_return", pd.NA)),
                "test_ann_return": float(test_stats.get("ann_return", pd.NA)),
                "test_sharpe": float(test_stats.get("sharpe", pd.NA)),
                "test_max_dd": float(test_stats.get("max_drawdown", pd.NA)),
            })
            if compute_regimes:
                test_df = df.loc[test_start:test_end]
                sig = make_signals(test_df, fast=best_fast, slow=best_slow)
                if execution == "close":
                    bt = backtest_close(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
                else:
                    bt = backtest_open(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
                vol = regimes_mod.realized_vol(test_df, window=vol_window)
                labels = regimes_mod.regime_labels_from_vol(vol, q=vol_q)
                perf_by_regime = regimes_mod.performance_by_regime(bt, labels)
                for _, r in perf_by_regime.iterrows():
                    regimes_rows.append({
                        "train_start": train_start,
                        "train_end": train_end,
                        "test_start": test_start,
                        "test_end": test_end,
                        "best_fast": int(best_fast),
                        "best_slow": int(best_slow),
                        "regime": int(r["regime"]),
                        "ann_return": float(r.get("ann_return", pd.NA)),
                        "ann_vol": float(r.get("ann_vol", pd.NA)),
                        "sharpe": float(r.get("sharpe", pd.NA)),
                        "max_drawdown": float(r.get("max_drawdown", pd.NA)),
                    })
        except Exception as e:
            rows.append({
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "error": str(e),
            })
    summary = pd.DataFrame(rows)
    if compute_regimes:
        regimes_df = pd.DataFrame(regimes_rows)
        return summary, regimes_df
    return summary
from typing import List, Tuple
import pandas as pd
import numpy as np
from datetime import timedelta

from signals import make_signals
from backtest import backtest_close, backtest_open
from metrics import perf_stats
import regimes as regimes_mod
from backtest import backtest_close, backtest_open


def _year_offset(dt: pd.Timestamp, years: int) -> pd.Timestamp:
    try:
        return dt.replace(year=dt.year + years)
    except Exception:
        # handle Feb 29 -> Feb 28
        return dt + pd.DateOffset(years=years)


def rolling_splits(dates: pd.DatetimeIndex, train_years: int = 7, test_years: int = 3) -> List[Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    """Create rolling train/test splits as (train_start, train_end, test_start, test_end).

    Splits are non-overlapping contiguous windows that advance by test_years each fold.
    """
    if not isinstance(dates, pd.DatetimeIndex):
        dates = pd.to_datetime(dates)

    start = dates.min()
    end = dates.max()

    folds: List[Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]] = []

    train_start = start
    train_end = _year_offset(train_start, train_years) - pd.Timedelta(days=1)
    while True:
        test_start = train_end + pd.Timedelta(days=1)
        test_end = _year_offset(test_start, test_years) - pd.Timedelta(days=1)
        if test_end > end:
            break
        folds.append((train_start, train_end, test_start, test_end))
        # advance windows by test_years
        train_start = _year_offset(train_start, test_years)
        train_end = _year_offset(train_start, train_years) - pd.Timedelta(days=1)

    return folds


def grid_search_train(df: pd.DataFrame, train_start: pd.Timestamp, train_end: pd.Timestamp, grid: List[Tuple[int, int]], execution: str = "close", fee_bps: float = 1.0, slippage_bps: float = 0.0) -> Tuple[int, int, dict]:
    """Grid-search on train window; return best (fast, slow) by annual return on strategy.
    Returns (best_fast, best_slow, metrics).
    """
    best = None
    best_metric = -np.inf
    train_df = df.loc[train_start:train_end]
    for fast, slow in grid:
        if slow <= fast:
            continue
        sig = make_signals(train_df, fast=fast, slow=slow)
        if execution == "close":
            bt = backtest_close(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
        elif execution == "open":
            bt = backtest_open(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
        else:
            raise ValueError(f"Unknown execution mode: {execution}")
        stats = perf_stats(bt["strat_ret"]) if "strat_ret" in bt else perf_stats(bt["ret"])
        ann = float(stats.get("ann_return", -np.inf) or -np.inf)
        if ann > best_metric:
            best_metric = ann
            best = (fast, slow, stats)

    if best is None:
        raise ValueError("No valid parameter combination found in grid")
    return best


def evaluate_params(df: pd.DataFrame, fast: int, slow: int, test_start: pd.Timestamp, test_end: pd.Timestamp, execution: str = "close", fee_bps: float = 1.0, slippage_bps: float = 0.0) -> dict:
    test_df = df.loc[test_start:test_end]
    sig = make_signals(test_df, fast=fast, slow=slow)
    if execution == "close":
        bt = backtest_close(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
    else:
        bt = backtest_open(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
    stats = perf_stats(bt["strat_ret"]) if "strat_ret" in bt else perf_stats(bt["ret"])
    return stats


def run_walkforward_for_ticker(df: pd.DataFrame, grid: List[Tuple[int, int]] = None, train_years: int = 7, test_years: int = 3, fee_bps: float = 1.0, slippage_bps: float = 0.0, execution: str = "close", compute_regimes: bool = False, vol_window: int = 21, vol_q: int = 4) -> pd.DataFrame:
    """Run rolling walk-forward on a single ticker price DataFrame.

    Returns a DataFrame summarizing each fold with selected params and test metrics.
    """
    if grid is None:
        # default reasonable grid
        grid = [(f, s) for f in range(5, 31, 5) for s in range(10, 61, 5)]

    idx = pd.to_datetime(df.index)
    folds = rolling_splits(idx, train_years=train_years, test_years=test_years)
    rows = []
    regimes_rows = []
    for train_start, train_end, test_start, test_end in folds:
        try:
            best_fast, best_slow, train_stats = grid_search_train(df, train_start, train_end, grid, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps)
            test_stats = evaluate_params(df, best_fast, best_slow, test_start, test_end, execution=execution, fee_bps=fee_bps, slippage_bps=slippage_bps)
            rows.append({
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "best_fast": int(best_fast),
                "best_slow": int(best_slow),
                "train_ann_return": float(train_stats.get("ann_return", np.nan)),
                "test_ann_return": float(test_stats.get("ann_return", np.nan)),
                "test_sharpe": float(test_stats.get("sharpe", np.nan)),
                "test_max_dd": float(test_stats.get("max_drawdown", np.nan)),
            })
            if compute_regimes:
                # compute full test backtest df to derive regime-level performance
                test_df = df.loc[test_start:test_end]
                sig = make_signals(test_df, fast=best_fast, slow=best_slow)
                if execution == "close":
                    bt = backtest_close(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)
                else:
                    bt = backtest_open(sig, fee_bps=fee_bps, slippage_bps=slippage_bps)

                # compute realized vol and regime labels on the test period
                vol = regimes_mod.realized_vol(test_df, window=vol_window)
                labels = regimes_mod.regime_labels_from_vol(vol, q=vol_q)
                perf_by_regime = regimes_mod.performance_by_regime(bt, labels)
                # attach fold metadata
                for _, r in perf_by_regime.iterrows():
                    regimes_rows.append({
                        "train_start": train_start,
                        "train_end": train_end,
                        "test_start": test_start,
                        "test_end": test_end,
                        "best_fast": int(best_fast),
                        "best_slow": int(best_slow),
                        "regime": int(r["regime"]),
                        "ann_return": float(r.get("ann_return", np.nan)),
                        "ann_vol": float(r.get("ann_vol", np.nan)),
                        "sharpe": float(r.get("sharpe", np.nan)),
                        "max_drawdown": float(r.get("max_drawdown", np.nan)),
                    })
        except Exception as e:
            rows.append({
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "error": str(e),
            })

    summary = pd.DataFrame(rows)
    if compute_regimes:
        regimes_df = pd.DataFrame(regimes_rows)
        return summary, regimes_df
    return summary
