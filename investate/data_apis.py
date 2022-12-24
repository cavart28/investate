import configparser
import datetime
import os
import requests
import json

from tiingo import TiingoClient
import robin_stocks.robinhood as r
import pandas_datareader as pdr

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


def get_intraday_data(ticker='QQQ',
                      api_key=myconfigs['tiingo']['api'],
                      start='2019-11-01',
                      end='2019-11-01'):
    headers = {'Content-Type': 'application/csv'}
    query_url = f'https://api.tiingo.com/iex/{ticker}/' \
                f'prices?startDate={start}&endDate={end}&resampleFreq=1min&token={api_key}'
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


def ts_to_date_string(ts, div=1, tz=datetime.timezone.utc):
    t = datetime.datetime.fromtimestamp(ts / div, tz=tz)
    return '{%Y-%m-%d %H:%M:%S.%f%z}'.format(t)


def turn_into_utc(date):
    """
    Add utc timezone if none exist, otherwise convert to UTC
    :param date: a datetime instance
    :return: converted/localized datetime
    """
    try:
        converted_date = date.tz_localize(tz=datetime.timezone.utc)
    except TypeError:
        converted_date = date.tz_convert(tz=datetime.timezone.utc)
    return converted_date


def normalize_to_utc_pd_timestamp(date):
    return pd.to_datetime(date, utc=True)


# TODO: Remove the pandas depreciation warning?
def fetch_data_and_cache(ticker,
                         start,
                         end,
                         source,
                         append_to_path='_daily',
                         fetch_func=pdr.get_data_tiingo,
                         date_col_name='date',
                         drop_duplicates=False,
                         **fetch_func_kwargs):
    """
    Get ticker data using the tiingo api (by default) if the data does not already exist locally in the source folder.
    The local source folder contains files with name in the format f'{ticker}_{freq}.csv'
    When get_tiingo_data is called, the range of the request is compared with the existing range in the
    corresponding local file (unless it does not exist, in which case the data is just fetched) and only
    the missing one is downloaded. The only assumption is that the range of date is continuous within
    the existing local file, and sorted. The assumption holds if the data is fetched with this function only
    because it always extends the existing range in a continuous manner, even when it is wasteful with
    respect to the query (e.g. existing data is [0, 10], query is [15, 20], the function will fetch and append
    the range [11, 20] to maintain continuity)

    drop_duplicates should NOT be needed but for some reason I have yet to decipher fully,
    fetch_data_and_cache will create duplicates when used with intraday data. The queried intervals look correct
    but for some reason (maybe due to timezones mis-conversion) the results of the query are repeating some of the
    terms. To see the problem, print the  query around line 136 (or debug) and not that they are correct
    yet the results of fetch_func contains redundant rows when fetch_func is get_intraday_data""
    """

    existing_files = os.listdir(source)
    existing_tickers_and_freq_str = [f[:-4] for f in existing_files]
    ticker_and_freq_str = ticker + append_to_path
    path_to_csv = os.path.join(source, f'{ticker_and_freq_str}.csv')

    ts_start = normalize_to_utc_pd_timestamp(start)
    ts_end = normalize_to_utc_pd_timestamp(end)

    if ticker_and_freq_str in existing_tickers_and_freq_str:
        ticker_df = pd.read_csv(path_to_csv, parse_dates=['date'], date_parser=normalize_to_utc_pd_timestamp)

        ts_existing_start = ticker_df['date'].iloc[0]
        ts_existing_end = ticker_df['date'].iloc[-1]

        ts_new_end = max(ts_existing_end, ts_end)
        ts_new_start = min(ts_existing_start, ts_start)

        left_query = (ts_new_start, ts_existing_start)
        right_query = (ts_existing_end, ts_new_end)

        for i, query in enumerate([left_query, right_query]):
            if len(set(query)) == 2:
                ts_start, ts_end = query
                result_df = fetch_func(ticker,
                                       start=ts_start,
                                       end=ts_end,
                                       **fetch_func_kwargs)

                result_df.reset_index(inplace=True)
                result_df['date'] = result_df[date_col_name].apply(normalize_to_utc_pd_timestamp)

                if date_col_name != 'date':
                    result_df.drop(date_col_name, axis=1, inplace=True)
                # Remove the last row of result_df since the query returns inclusive upper bound
                if i == 0:
                    ticker_df = pd.concat(objs=(result_df.iloc[:-1], ticker_df), ignore_index=True)
                else:
                    ticker_df = pd.concat(objs=(ticker_df, result_df.iloc[1:]), ignore_index=True)
                ticker_df.reset_index(inplace=True, drop=True)

    else:
        ticker_df = fetch_func(ticker,
                               start=start,
                               end=end,
                               **fetch_func_kwargs)
        ticker_df.reset_index(inplace=True)
        # standardise the name of the date column and its format
        ticker_df['date'] = ticker_df[date_col_name].apply(normalize_to_utc_pd_timestamp)
        if date_col_name != 'date':
            ticker_df.drop(date_col_name, axis=1, inplace=True)
    if drop_duplicates:
        ticker_df = ticker_df.drop_duplicates('date')
        ticker_df.reset_index(inplace=True, drop=True)

    ticker_df.to_csv(path_to_csv, index=False)
    return ticker_df


def fetch_data_and_cache_repeatively(ticker,
                                     start,
                                     end,
                                     source,
                                     append_to_path='_daily',
                                     fetch_func=pdr.get_data_tiingo,
                                     date_col_name='date',
                                     max_try=3,
                                     verbose=True,
                                     **fetch_func_kwargs):
    """
    Some apis will silently limit the amount of data they return.
    This function is essentially calling fetch_data_and_cache until the full range of the query
    is cached or until the calls are not brining anymore data. This could happen if the some call quota are exceeded
    or if the query dates are weekend/holidays. There could be other reasons, the point here it to make sure the
    function terminates.
    """
    ticker_df = fetch_data_and_cache(ticker,
                                     start,
                                     end,
                                     source,
                                     append_to_path,
                                     fetch_func,
                                     date_col_name,
                                     drop_duplicates=True,
                                     **fetch_func_kwargs)

    existing_start = normalize_to_utc_pd_timestamp(ticker_df.date.iloc[0])
    existing_end = normalize_to_utc_pd_timestamp(ticker_df.date.iloc[-1])
    start = normalize_to_utc_pd_timestamp(start)
    end = normalize_to_utc_pd_timestamp(end)

    tries = 1
    while (start < existing_start or existing_end < end) and tries < max_try:
        if verbose:
            print(f"Attempt number {tries}")

        ticker_df = fetch_data_and_cache(ticker,
                                         start,
                                         end,
                                         source,
                                         append_to_path,
                                         fetch_func,
                                         date_col_name,
                                         drop_duplicates=True,
                                         **fetch_func_kwargs)
        if existing_start == ticker_df.date.iloc[0] and existing_end == ticker_df.date.iloc[-1]:
            tries = max_try
            if verbose:
                print(f"The data is not changing with new calls, either the data is complete or the calls are "
                      f"not bringing anything new. This could happen if one or more of the query dates "
                      f"are weekends or holidays.")
        else:
            existing_start = ticker_df.date.iloc[0]
            existing_end = ticker_df.date.iloc[-1]
            tries += 1

    return ticker_df.drop_duplicates('date')
