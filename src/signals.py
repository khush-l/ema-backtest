import pandas as pd

# Exponential moving average (pandas EWM)
def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

# Add EMA columns and a binary long signal (1 if fast>slow)
def make_signals(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.DataFrame:
    out = df.copy()
    out["ema_fast"] = ema(out["Close"], fast)
    out["ema_slow"] = ema(out["Close"], slow)
    out["signal"] = (out["ema_fast"] > out["ema_slow"]).astype(int)
    return out.dropna()
import pandas as pd

# Exponential moving average (pandas EWM)
def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

# Add EMA columns and a binary long signal (1 if fast>slow)
def make_signals(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.DataFrame:
    """Add ema_fast, ema_slow and signal columns to df.

    signal = 1 when ema_fast > ema_slow, else 0. Uses Close price.
    """
    out = df.copy()
    out["ema_fast"] = ema(out["Close"], fast)
    out["ema_slow"] = ema(out["Close"], slow)
    out["signal"] = (out["ema_fast"] > out["ema_slow"]).astype(int)
    return out.dropna()
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def make_signals(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.DataFrame:
    """Add ema_fast, ema_slow and signal columns to df.

    signal = 1 when ema_fast > ema_slow, else 0. Uses Close price.
    """
    out = df.copy()
    out["ema_fast"] = ema(out["Close"], fast)
    out["ema_slow"] = ema(out["Close"], slow)
    out["signal"] = (out["ema_fast"] > out["ema_slow"]).astype(int)
    return out.dropna()
