# Minimal runner to execute the EMA pipeline and plot equity vs buy-and-hold
from typing import List
import matplotlib.pyplot as plt

from data import download_prices
from signals import make_signals
from backtest import backtest_close
from metrics import perf_stats


DEFAULT_TICKERS: List[str] = ["SPY", "QQQ", "IWM", "TLT", "GLD"]


def run_one(ticker: str = "SPY", fast: int = 12, slow: int = 26, fee_bps: float = 1.0):
    px = download_prices(ticker)
    sig = make_signals(px, fast=fast, slow=slow)
    bt = backtest_close(sig, fee_bps=fee_bps)

    stats = perf_stats(bt["strat_ret"]) if "strat_ret" in bt else perf_stats(bt["ret"])
    print(ticker, {k: round(v, 6) if isinstance(v, float) else v for k, v in stats.items()})

    ax = bt[["equity", "buyhold"]].plot(title=f"{ticker} EMA({fast},{slow}) equity vs buy&hold")
    ax.set_ylabel("Cumulative return")
    plt.tight_layout()
    plt.show()


# Run the strategy for a list of tickers
def main(tickers: List[str] = DEFAULT_TICKERS):
    for t in tickers:
        try:
            run_one(ticker=t, fast=12, slow=26, fee_bps=2.0)
        except Exception as e:
            print(f"{t} failed: {e}")


if __name__ == "__main__":
    main()
"""Simple runner for the EMA crossover backtest (close-to-close v1).

Run directly or import functions from modules in `src/`.
"""
from typing import List
import matplotlib.pyplot as plt

from data import download_prices
from signals import make_signals
from backtest import backtest_close
from metrics import perf_stats


DEFAULT_TICKERS: List[str] = ["SPY", "QQQ", "IWM", "TLT", "GLD"]


def run_one(ticker: str = "SPY", fast: int = 12, slow: int = 26, fee_bps: float = 1.0):
    px = download_prices(ticker)
    sig = make_signals(px, fast=fast, slow=slow)
    bt = backtest_close(sig, fee_bps=fee_bps)

    stats = perf_stats(bt["strat_ret"]) if "strat_ret" in bt else perf_stats(bt["ret"])
    print(ticker, {k: round(v, 6) if isinstance(v, float) else v for k, v in stats.items()})

    ax = bt[["equity", "buyhold"]].plot(title=f"{ticker} EMA({fast},{slow}) equity vs buy&hold")
    ax.set_ylabel("Cumulative return")
    plt.tight_layout()
    plt.show()


def main(tickers: List[str] = DEFAULT_TICKERS):
    for t in tickers:
        try:
            run_one(ticker=t, fast=12, slow=26, fee_bps=2.0)
        except Exception as e:
            print(f"{t} failed: {e}")


if __name__ == "__main__":
    main()
