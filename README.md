EMA Crossover Backtest (MVP)

Purpose

Minimal, script-based implementation of an EMA crossover backtest with:
- close-to-close and next-day-open execution modes
- configurable transaction costs and slippage (bps)
- walk-forward evaluation and regime (volatility) slicing

Quick start

1. Create and activate a virtualenv, then install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the basic example (plots will open):

```bash
python src/run.py
```

Aggregate walk-forward across the default universe and save results/figures:

```bash
python src/results.py
```

Project layout

- `src/data.py` — price download helpers
- `src/signals.py` — EMA and signal generation
- `src/backtest.py` — close/open backtests with fees/slippage
- `src/metrics.py` — performance statistics
- `src/walkforward.py` — rolling walk-forward and grid search
- `src/regimes.py` — realized vol and regime-level perf
- `src/plotting.py` — plotting helpers
- `src/results.py` — aggregate runner that saves CSVs and figures

Notes

- This repo is an MVP intended for local experimentation. It requires internet access to download prices via yfinance.
- To push to GitHub: initialize a git repo, create a remote, and push (commands provided below).

Push to GitHub (example commands)

```bash
cd /Users/khushl/Documents/ema-backtest
git init
git add .
git commit -m "MVP: EMA crossover backtest"
# create an empty repo on GitHub first, then add the remote and push:
git remote add origin git@github.com:<your-username>/ema-backtest.git
git push -u origin main
```
# EMA Crossover Backtest

Quant-style EMA crossover backtest project (v1).

Features:

- Close-to-close EMA crossover strategy implementation.
- Transaction costs (basis points).
- Avoids lookahead by shifting signals.
- Comparison vs buy-and-hold.

Next steps (planned): walk-forward testing, regime slicing, next-day open execution.

How to run (after installing requirements):

1. Create a virtualenv and install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the starter script:

```bash
python src/run.py
```

Files:

- `src/data.py` - download price data (yfinance wrapper)
- `src/signals.py` - EMA and signal generation
- `src/backtest.py` - close-to-close backtest engine
- `src/metrics.py` - performance metrics
- `src/run.py` - small CLI/runner to execute the pipeline
