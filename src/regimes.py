import pandas as pd
import numpy as np

from metrics import perf_stats


def realized_vol(df: pd.DataFrame, window: int = 21, periods_per_year: int = 252) -> pd.Series:
    # Rolling annualized volatility of Close returns
    close = df["Close"]
    if hasattr(close, "ndim") and getattr(close, "ndim") > 1:
        close = close.iloc[:, 0]
    ret = close.pct_change()
    rv = ret.rolling(window).std() * (periods_per_year ** 0.5)
    return rv


def regime_labels_from_vol(vol: pd.Series, q: int = 4) -> pd.Series:
    # Bucket vol into q quantile regimes (1..q)
    valid = vol.dropna()
    if len(valid) == 0:
        return pd.Series(index=vol.index, data=pd.NA)
    try:
        labels = pd.qcut(valid, q, labels=False) + 1
        return labels.reindex(vol.index)
    except Exception:
        try:
            vals = valid.values
            pct = np.nanpercentile(vals, np.linspace(0, 100, q + 1))
            bins = np.unique(pct)
            if len(bins) <= 1:
                return pd.Series(index=vol.index, data=pd.NA)
            labels = pd.cut(valid, bins=bins, labels=False, include_lowest=True) + 1
            return labels.reindex(vol.index)
        except Exception:
            return pd.Series(index=vol.index, data=pd.NA)


def performance_by_regime(bt_df: pd.DataFrame, regime_series: pd.Series) -> pd.DataFrame:
    # Compute perf_stats per regime label for a backtest DataFrame
    rows = []
    labels = regime_series.rename("regime").reindex(bt_df.index)
    if labels.dropna().empty:
        return pd.DataFrame(rows)
    for regime in sorted(labels.dropna().unique()):
        mask = labels == regime
        try:
            stats = perf_stats(bt_df.loc[mask, "strat_ret"].dropna())
        except Exception:
            stats = {"ann_return": float("nan"), "ann_vol": float("nan"), "sharpe": float("nan"), "max_drawdown": float("nan")}
        row = {"regime": int(regime)}
        row.update(stats)
        rows.append(row)
    return pd.DataFrame(rows)
from typing import Tuple
import pandas as pd
import numpy as np

from metrics import perf_stats


def realized_vol(df: pd.DataFrame, window: int = 21, periods_per_year: int = 252) -> pd.Series:
    """Compute rolling realized volatility (annualized) on Close returns.

    Returns a Series aligned with df.index.
    """
    close = df["Close"]
    # if Close is a DataFrame (multi-column), reduce to first column
    if hasattr(close, "ndim") and getattr(close, "ndim") > 1:
        close = close.iloc[:, 0]
    ret = close.pct_change()
    rv = ret.rolling(window).std() * (periods_per_year ** 0.5)
    return rv


def regime_labels_from_vol(vol: pd.Series, q: int = 4) -> pd.Series:
    """Bucket vol series into q quantile regimes (1..q), 1=lowest vol."""
    # Dropna before qcut, then reindex
    valid = vol.dropna()
    if len(valid) == 0:
        return pd.Series(index=vol.index, data=pd.NA)
    try:
        labels = pd.qcut(valid, q, labels=False) + 1
        return labels.reindex(vol.index)
    except Exception:
        # Fallback: use percentile-based cut if qcut fails
        try:
            vals = valid.values
            pct = np.nanpercentile(vals, np.linspace(0, 100, q + 1))
            # create bins from percentiles (ensure unique bin edges)
            bins = np.unique(pct)
            if len(bins) <= 1:
                return pd.Series(index=vol.index, data=pd.NA)
            labels = pd.cut(valid, bins=bins, labels=False, include_lowest=True) + 1
            return labels.reindex(vol.index)
        except Exception:
            return pd.Series(index=vol.index, data=pd.NA)


def performance_by_regime(bt_df: pd.DataFrame, regime_series: pd.Series) -> pd.DataFrame:
    """Compute perf_stats per regime label for a backtest DataFrame (expects 'strat_ret')."""
    rows = []
    # align regime labels to backtest index
    labels = regime_series.rename("regime").reindex(bt_df.index)
    if labels.dropna().empty:
        return pd.DataFrame(rows)

    for regime in sorted(labels.dropna().unique()):
        mask = labels == regime
        try:
            stats = perf_stats(bt_df.loc[mask, "strat_ret"].dropna())
        except Exception:
            stats = {"ann_return": float("nan"), "ann_vol": float("nan"), "sharpe": float("nan"), "max_drawdown": float("nan")}
        row = {"regime": int(regime)}
        row.update(stats)
        rows.append(row)
    return pd.DataFrame(rows)
