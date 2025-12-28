import numpy as np
import pandas as pd

# Return simple performance stats: ann_return, ann_vol, sharpe, max_drawdown
def perf_stats(strat_ret: pd.Series, periods_per_year: int = 252) -> dict:
    r = strat_ret.fillna(0.0)
    if len(r) <= 1:
        return {"ann_return": np.nan, "ann_vol": np.nan, "sharpe": np.nan, "max_drawdown": np.nan}

    cumulative = (1 + r).cumprod()
    total_periods = len(r)
    ann_ret = cumulative.iloc[-1] ** (periods_per_year / total_periods) - 1
    ann_vol = r.std() * np.sqrt(periods_per_year)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan

    peak = cumulative.cummax()
    drawdown = cumulative / peak - 1
    max_dd = drawdown.min()

    return {"ann_return": ann_ret, "ann_vol": ann_vol, "sharpe": sharpe, "max_drawdown": max_dd}
import numpy as np
import pandas as pd


def perf_stats(strat_ret: pd.Series, periods_per_year: int = 252) -> dict:
    r = strat_ret.fillna(0.0)
    if len(r) <= 1:
        return {"ann_return": np.nan, "ann_vol": np.nan, "sharpe": np.nan, "max_drawdown": np.nan}

    cumulative = (1 + r).cumprod()
    total_periods = len(r)
    ann_ret = cumulative.iloc[-1] ** (periods_per_year / total_periods) - 1
    ann_vol = r.std() * np.sqrt(periods_per_year)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan

    peak = cumulative.cummax()
    drawdown = cumulative / peak - 1
    max_dd = drawdown.min()

    return {"ann_return": ann_ret, "ann_vol": ann_vol, "sharpe": sharpe, "max_drawdown": max_dd}
