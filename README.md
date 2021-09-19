# Backtest_Supertrend
Codes for Medium article "Backtest Supertrend Trading Strategy in Elasticsearch" in Medium
(https://wire.insiderfinance.io/backtest-supertrend-crossover-strategy-with-elasticsearch-ab048a3c6b8)


The following steps have been tested with Elasticsearch Server v7.10.1

1. Create an index, fidelity28_fund and the corresponding data are populated. The data for the index, fidelity28_fund, is coming from IEX (Investors Exchange) with the 28 Fidelity commission-free ETFs selected for demo purpose. The time range picked is between 2020-12-15 and 2021-05-31.

$ ./fidelity28_index.sh

2. Assume you have installed python 3.7, run the following command to go to virtual environment and prepare the python packages needed.

source venv/bin/activate

$ pip install -r requirements.txt

3. After the indices are created and the data are populated, You can try different ticker symbol such as FDEV, FMAT, FTEC, FHLC, FENY, FSTA, FDIS, FQAL, FDLO, FDMO and FUTY to backtest the RSI trading strategy. A report will be shown for the statistical data.

$ ./backtest_supertrend.sh -i backtest_supertrend.json -s FDEV -b 2021-02-01 -e 2021-05-31

You can follow the backtest_supertrend.json to rewrite a new trading strategy
