import requests
import json
import sys, getopt
from pprint import pprint
from datetime import datetime, timedelta

iex_date_pattern = '%Y-%m-%d'

# get data from elasticsearch server 
def get_data(input_file, start_date, end_date, symbol):
    url = 'http://localhost:9200/fidelity28_fund/_search?pretty'
    with open(input_file) as f:
        payload = json.load(f)
    payload_json = json.dumps(payload)
    start_datetime = datetime.strptime(start_date, iex_date_pattern)
    new_start_datetime = start_datetime - timedelta(days=45)
    new_start_date = new_start_datetime.strftime(iex_date_pattern)
    payload_json = payload_json % (new_start_date, end_date, symbol)
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload_json, headers=headers)
    return r.text


# get the command line parameters for the trading policy and the ticker symbol
def get_opt(argv):
    input_file = ''
    symbol = ''
    start_date = ''
    end_date = ''

    try:
        opts, args = getopt.getopt(argv, "hi:s:b:e:")
    except getopt.GetoptError:
        print('backtest_supertrend -i <inputfile> -s <symbol> -b <start date> -e <end date>')
        print('example: backtest_supertrend -i backtest_supertrend.json -s FDEV')
        sys.exit(-1)

    for opt, arg in opts:
        if opt == '-h':
            print('backtest_supertrend -i <inputfile> -s <symbol> -b <start date> -e <end date>')
            print('example: backtest_supertrend -i backtest_supertrend.json -s FDEV')
            sys.exit(0)
        elif opt == '-i':
            input_file = arg
        elif opt == '-s':
            symbol = arg
        elif opt == '-b':
            start_date = arg
        elif opt == '-e':
            end_date = arg

    if input_file == '' or start_date == '' or end_date == '' or symbol == '':
        print("Given value is invalid such as no input file, no start, end date or symbol!")
        sys.exit(-1)
    print("input_file '%s', start_date '%s', end_Date '%s', symbol '%s'" % (input_file, start_date, end_date, symbol))
    return input_file, start_date, end_date, symbol


def parse_data(resp, start_date):
    result = json.loads(resp)
    aggregations = result['aggregations']
    if aggregations and 'Backtest_Supertrend' in aggregations:
        backtest_supertrend = aggregations['Backtest_Supertrend']

    transactions = []
    if backtest_supertrend and 'buckets' in backtest_supertrend:
        hold = False
        psband = -1
        for bucket in backtest_supertrend['buckets']:
            transaction = {'buy_or_sell': 'hold', 'original': 'hold', 'date': bucket['key_as_string'],
                           'Daily': bucket['Daily']['value']}
            close = transaction['Daily']
            pclose = bucket['PClose']['value']
            buband = bucket['BUBand']['value']
            blband = bucket['BLBand']['value']

            fuband = buband if psband < 0 or buband < pfuband or pclose > pfuband else pfuband
            flband = blband if psband < 0 or blband > pflband or pclose < pflband else pflband
            if psband == -1:
                sband = fuband
            else:
                if psband == pfuband:
                    if close < fuband:
                        sband = fuband
                    elif close > fuband:
                        sband = flband
                elif psband == pflband:
                    if close > flband:
                        sband = flband
                    elif close < flband:
                        sband = fuband

            if transaction['date'] >= start_date:
                if psband > pclose and sband < close:
                    transaction['original'] = 'buy'
                    transaction['buy_or_sell'] = 'buy' if not hold else 'hold'
                    hold = True
                elif psband < pclose and sband > close:
                    transaction['original'] = 'sell'
                    transaction['buy_or_sell'] = 'sell' if hold else 'hold'
                    hold = False

                transactions.append(transaction)

            psband = sband
            pfuband = fuband
            pflband = flband
    return transactions


def report(transactions, type):
    print('Transaction Sequence for : ' + type)
    print('-' * 80)
    pprint(transactions, width=120)
    print('-' * 80)
    print()

    profit = 0.0;
    num_of_buy = 0
    num_of_sell = 0
    buy_price = 0;
    win = 0
    lose = 0
    max_buy_price = 0
    for transaction in transactions:
        if transaction['buy_or_sell'] == 'buy':
           num_of_buy += 1
           buy_price = transaction['Daily']
           profit -= transaction['Daily']
           max_buy_price = transaction['Daily'] if max_buy_price < transaction['Daily'] else max_buy_price
        elif transaction['buy_or_sell'] == 'sell' and buy_price > 0:
           profit += transaction['Daily']
           if transaction['Daily'] > buy_price:
               win += 1
           else:
               lose += 1
           buy_price = 0
           num_of_sell += 1

    if buy_price > 0:
        profit += transactions[-1]['Daily']
        if transaction['Daily'] > buy_price:
            win += 1
        else:
            lose += 1

    print('number of buy:      %8d' % (num_of_buy))
    print('number of sell:     %8d' % (num_of_sell))
    print('number of win:      %8d' % (win))
    print('number of lose:     %8d' % (lose))
    print('total profit:       %8.2f' % (profit))
    if num_of_buy > 0:
        print('profit/transaction: %8.2f' % (profit/num_of_buy))
    print('maximum buy price:  %8.2f' % max_buy_price)
    if max_buy_price > 0:
        print('profit percent:     %8.2f%%' % (profit*100/max_buy_price))


def main(argv):
    type = 'Supertrend'
    input_file, start_date, end_date, symbol = get_opt(argv)
    resp = get_data(input_file, start_date, end_date, symbol)
    transactions = parse_data(resp, start_date)
    report(transactions, type)


if __name__ == '__main__':
    main(sys.argv[1:])
