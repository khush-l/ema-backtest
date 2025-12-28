from typing import List, Dict
import pandas as pd
import yfinance as yf

# Download OHLCV prices for a single ticker
def download_prices(ticker: str, start: str = "2012-01-01") -> pd.DataFrame:
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    df = df.rename(columns=str.title)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()

# Download prices for multiple tickers and return a dict
def download_universe(tickers: List[str], start: str = "2012-01-01") -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}
    for t in tickers:
        out[t] = download_prices(t, start=start)
    return out
from typing import List, Dict
import pandas as pd
import yfinance as yf


def download_prices(ticker: str, start: str = "2012-01-01") -> pd.DataFrame:
    """Download OHLCV prices for a ticker using yfinance.

    Returns a DataFrame with columns: Open, High, Low, Close, Volume (auto_adjust=True).
    """
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    # Normalize column names to Title case (yfinance returns uppercase)
    df = df.rename(columns=str.title)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()


def download_universe(tickers: List[str], start: str = "2012-01-01") -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}
    for t in tickers:
        out[t] = download_prices(t, start=start)
    return out
