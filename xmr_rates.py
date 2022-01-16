import psycopg2
import requests
import time

conn = psycopg2.connect('dbname=xmrapi user=exchangerates host=127.0.0.1 password=xxx')

"""
CREATE TABLE IF NOT EXISTS exchange_rates (
	coin VARCHAR(5) NOT NULL,
	currency VARCHAR(5) NOT NULL,
	price NUMERIC(6, 2) NOT NULL,
	timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def update_exchange_rates():
    prices = []

    # coingecko
    try:
        r = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids=monero')
        r.raise_for_status()
        data = r.json()
        prices.append(data[0]['current_price'])
    except:
        print('Coingecko API unavailable')

    # coinmarketcap
    headers = {
        'X-CMC_PRO_API_KEY': 'xxx'
    }
    params = {
        'slug': 'monero',
        'convert': 'EUR'
    }
    try:
        r = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest', params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        quote = data['data']['328']['quote']
        prices.append(quote['EUR']['price'])
    except:
        print('Coinmarketcap API unavailable')

    # coinranking
    headers = {
        'X-Access-Token': 'xxx',
    }
    params = {
        'referenceCurrencyUuid': '5k-_VTxqtCEI' # EUR
    }
    try:
        r = requests.get('https://api.coinranking.com/v2/coin/3mVx2FX_iJFp5/price', params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        prices.append(float(data['data']['price']))
    except:
        print('Coinranking API unavailable')

    # calculate average
    avg = sum(prices) / len(prices)
    avg = round(avg, 2)
    print('avg: 1 XMR = ' + str(avg) + ' EUR')

    cur = conn.cursor()
    cur.execute("INSERT INTO exchange_rates VALUES ('XMR', 'EUR', '" + str(avg) + "')")
    conn.commit()

while True:
    update_exchange_rates()

    cur = conn.cursor()
    cur.execute("SELECT price FROM exchange_rates WHERE coin = 'XMR' AND currency = 'EUR' ORDER BY timestamp DESC LIMIT 1")
    print('pgsql: 1 XMR = ' + str(cur.fetchone()[0]) + ' EUR')

    time.sleep(60 * 15)
