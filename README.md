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
