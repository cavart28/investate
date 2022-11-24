import configparser
from tiingo import TiingoClient
import robin_stocks.robinhood as r
import requests
import json
import pandas as pd

config_path = '/Users/cavart/fi.ini'
myconfigs = configparser.ConfigParser()
myconfigs.read(config_path)

# see https://algotrading101.com/learn/robinhood-api-guide/
def login_robinhod():
    robin_config = myconfigs['robin']
    r.login(username=robin_config['user'],
            password=robin_config['password'],
            expiresIn=86400,
            by_sms=True)

# Tiingo api setup
# https://tiingo-python.readthedocs.io/en/latest/readme.html#usage
tiingo_config = {}
tiingo_config['session'] = True
tiingo_config['api_key'] = myconfigs['tiingo']['api']
tiingo_client = TiingoClient(tiingo_config)


# Example of getting intraday data with Tiingo
def response_to_df(response):
    return pd.DataFrame(json.loads(response.text))


def get_intraday_data(ticker='QQQ', tiingo_token=myconfigs['tiingo']['api'], start_date='2022-01-01'):
    headers = {'Content-Type': 'application/csv'}
    query_url = f'https://api.tiingo.com/iex/{ticker}/prices?startDate={start_date}&resampleFreq=5min&token={tiingo_token}'
    requestResponse = requests.get(query_url,
                                   headers=headers)
    return response_to_df(requestResponse)


# iex
iex_token = myconfigs['iex']['token']
iex_workspace = myconfigs['iex']['workspace']

# Example url:
# url = f'https://cloud.iexapis.com/stable/tops?token={iex_token}&symbols=aapl'
# response = requests.get(url)
# response.content
