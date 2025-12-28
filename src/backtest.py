import pandas as pd

# Close-to-close backtest using shifted signals; returns df with strat_ret/equity
def backtest_close(df: pd.DataFrame, fee_bps: float = 1.0, slippage_bps: float = 0.0) -> pd.DataFrame:
    import pandas as pd


    # Close-to-close backtest using shifted signals; returns df with strat_ret/equity
    def backtest_close(df: pd.DataFrame, fee_bps: float = 1.0, slippage_bps: float = 0.0) -> pd.DataFrame:
        out = df.copy()
        out["ret"] = out["Close"].pct_change().fillna(0.0)
        out["pos"] = out["signal"].shift(1).fillna(0).astype(int)
        out["turnover"] = out["pos"].diff().abs().fillna(0)
        fee = fee_bps / 10000.0
        slippage = slippage_bps / 10000.0
        out["cost"] = out["turnover"] * (fee + slippage)
        out["strat_ret"] = out["pos"] * out["ret"] - out["cost"]
        out["equity"] = (1.0 + out["strat_ret"]).cumprod()
        out["buyhold"] = (1.0 + out["ret"]).cumprod()
        return out


    # Next-day open execution backtest; strat_ret uses open->close intraday returns
    def backtest_open(df: pd.DataFrame, fee_bps: float = 1.0, slippage_bps: float = 0.0) -> pd.DataFrame:
        out = df.copy()
        out["oc_ret"] = (out["Close"] / out["Open"] - 1.0).fillna(0.0)
        out["pos"] = out["signal"].shift(1).fillna(0).astype(int)
        out["turnover"] = out["pos"].diff().abs().fillna(0)
        fee = fee_bps / 10000.0
        slippage = slippage_bps / 10000.0
        out["cost"] = out["turnover"] * (fee + slippage)
        out["strat_ret"] = out["pos"] * out["oc_ret"] - out["cost"]
        out["equity"] = (1.0 + out["strat_ret"]).cumprod()
        out["ret"] = out["Close"].pct_change().fillna(0.0)
        out["buyhold"] = (1.0 + out["ret"]).cumprod()
        return out
        out["equity"] = (1.0 + out["strat_ret"]).cumprod()
