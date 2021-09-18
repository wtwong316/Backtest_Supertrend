#!/bin/bash
source ./venv/bin/activate
pip install -r requirements.txt
python backtest_supertrend.py $*

