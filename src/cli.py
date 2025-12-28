#!/usr/bin/env python3
# Small CLI wrapper to run the results runner
import argparse
import sys
import os

# when running `python src/cli.py` the script's directory is `src/`, so importing `results` will import `src/results.py`.
import results


def parse_args():
    p = argparse.ArgumentParser(description="Run EMA backtest aggregate runner")
    p.add_argument("--tickers", "-t", default="SPY,QQQ,IWM,TLT,GLD", help="Comma-separated tickers")
    p.add_argument("--start", default="2012-01-01", help="Start date for historical data (YYYY-MM-DD)")
    p.add_argument("--execution", choices=["close", "open"], default="close", help="Execution mode")
    p.add_argument("--fee-bps", type=float, default=1.0, help="Fee in basis points per trade")
    p.add_argument("--slippage-bps", type=float, default=0.0, help="Slippage in basis points")
    p.add_argument("--no-regimes", dest="compute_regimes", action="store_false", help="Do not compute regimes (faster)")
    p.add_argument("--outdir", default=None, help="Optional output directory for results (overrides default 'results')")
    return p.parse_args()


def main():
    args = parse_args()
    universe = [s.strip().upper() for s in args.tickers.split(",") if s.strip()]

    # call run_aggregate in results.py and pass outdir explicitly
    outdir = results.run_aggregate(
        universe,
        start=args.start,
        execution=args.execution,
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
        compute_regimes=args.compute_regimes,
        outdir=args.outdir,
    )
    print(f"Done. results folder: {outdir}")


if __name__ == "__main__":
    main()
