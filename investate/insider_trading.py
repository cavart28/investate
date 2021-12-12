import requests
import pandas as pd
import progressbar
from time import sleep
from dateutil.parser import *
from dateutil.relativedelta import *
from tiingo import TiingoClient
import pandas_datareader as pdr
from py2store import myconfigs
from investate.file_utils import *


# each page has 20 rows, each is one insider purchase
def get_insider_df(n_pages=500,
                   n_per_page=20,
                   base_url='https://www.insidermonkey.com/insider-trading/purchases/',
                   save_to='',
                   wait_between_call_sec=None):
    """
    Function to get insider trading info from insidermonkey.com

    :param n_pages: number of webpage to get, starting from most recent
    :param n_per_page: number of insider trades per page on insidermonkey, 20 at the momment
    :param base_url: the url of the first page (most recent) insider trades
    :param save_to: location where to save the csv
    :param wait_between_call_sec: time in second to have python pause between api calls. May be useful to bypass api
    quota
    :param verbose: whether to print some form of progress, nice to see something is happening on long run
    :param n_page_per_print: number of pages after which the idx of the page is returned, to show progress. Only used
    if verbose is set to True
    :return: a dataframe of the results. The dataframe is also saved for convenience.
    """

    # Get the list of urls required to fetch the data
    urls = [base_url] + [base_url + f'{i}/' for i in range(0, n_per_page * n_pages, n_per_page)]
    all_dfs = []
    # since it can take a while, display a progress bar
    bar = progressbar.ProgressBar(maxval=n_pages,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ',
                                           progressbar.Percentage()])
    bar.start()
    for idx, url in enumerate(urls):
        try:
            html = requests.get(url).content
            df_list = pd.read_html(html)
            df = df_list[0]
            all_dfs.append(df)
            # just in case the insider monkey api has some form of query limit
            if wait_between_call_sec is not None:
                sleep(wait_between_call_sec)
            bar.update(idx)
        except Exception as e:
            print(e)
    bar.finish()

    # make a pandas df with the data
    df = pd.concat(all_dfs).reset_index(drop=True)
    df.sort_values('Date')
    # remove the $ sign and the commas from the price and turn it into a float
    df['Price'] = df['Price'].apply(lambda x: float(x[1:].replace(',', '')))
    df['Date'] = pd.to_datetime(df['Date'])
    # remove the timezone info, more convenient for later use and precision up to one day is not useful
    df['Date'] = df['Date'].apply(lambda x: x.replace(tzinfo=None))
    if save_to:
        df.to_csv(save_to)
    return df


def get_ticker_data_around_date(ticker: str,
                                start_date: str,
                                tiingo_api_key: str,
                                end_date=None,
                                length_in_days=180):
    """
    Use Tiingo to access stock basic info from the startdate until the endate (or startdate + length_in_days if enddate
    is None)
    :param ticker: str, the ticker name of the stock
    :param start_date: str or datetime date, the date starting at which the data will be pulled
    :param end_date: str, the last date at which the data will be pulled
    :param length_in_days: int, the number of days
    :param api_key: str, your tiingo opi key
    :return: a panda df of the stock basic stats from startdate to enddate
    """

    if isinstance(start_date, str):
        start_date = parse(start_date)
    config = {}
    # To reuse the same HTTP Session across API calls (and have better performance), include a session key
    config['session'] = True
    config['api_key'] = tiingo_api_key
    # Initialize
    client = TiingoClient(config)
    if end_date is None:
        rel_delt = relativedelta(days=+length_in_days)
        end_date = start_date + rel_delt
    tick_df = pdr.get_data_tiingo(ticker, start=start_date, end=end_date,
                                  pause=0.2, api_key=config['api_key'])
    return tick_df


def get_info_for_row(row, api_key, end_date=None, length_in_days=180):
    """
    Helper function getting the data for a specific row of the insider_df returned by get_insider_df
    :param row: a series, a row from get_insider_df
    :param end_date: str, the end date of given
    :param length_in_days: the number of days to span with the data to fetch
    :return: a pandas df
    """

    ticker = row['Symbol']
    start_date = row['Date']
    return get_ticker_data_around_date(ticker, start_date=start_date, api_key=api_key,
                                       end_date=end_date, length_in_days=length_in_days)


def get_insider_purchase_performance(insider_monkey_df,
                                     api_key,
                                     min_total_trigger=1e6,
                                     length_in_days=180,
                                     save_to=''):
    """
    Go through each row of insider_monkey_df, attempt to fetch the stock stats and find the highest growth
    starting from the date of the insider investment up to length_in_days many more days
    """
    results = []
    # group by company and date
    g = insider_monkey_df.groupby(['Company', 'Date'])
    ngroups = g.ngroups
    bar = progressbar.ProgressBar(maxval=ngroups,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ',
                                           progressbar.Percentage()])
    bar.start()
    for idx, (group, group_df) in enumerate(g):
        # find the total invested for the date
        group_df['total'] = group_df['Price'] * group_df['Amount']
        total_invested = group_df['total'].sum()
        # consider only large investments
        if total_invested > min_total_trigger:
            try:
                # we will use the first investment of the day to find the value of the stock and the date
                row = group_df.iloc[0]
                # get the stock values during the period of interest
                days_after_invest_df = get_info_for_row(row, api_key=api_key, length_in_days=length_in_days)
                # find the mac value during that time
                max_val = days_after_invest_df['close'].max()
                row_of_max = days_after_invest_df[days_after_invest_df['close'] == max_val]
                # determine the max growth
                max_growth = max_val / days_after_invest_df.iloc[0]['close'] - 1
                # the index of row_of_max is a multi-index, we extract the date from there
                day_of_max = row_of_max.index[0][1].replace(tzinfo=None)
                day_invested = row['Date'].replace(tzinfo=None)
                # this is how many days it took to reach the max, from the day of initial investment
                days_to_reach_max = day_of_max - day_invested
                results.append({'ticker': row['Symbol'],
                                'day_invested': day_invested,
                                'max_growth': max_growth,
                                'n days to max': days_to_reach_max, })
                bar.update(idx)
            except Exception as e:
                print(e)
    bar.finish()
    insider_purchase_return = pd.DataFrame(results)
    if save_to:
        insider_purchase_return.to_csv(save_to)

    return insider_purchase_return


def pull_data_for_tickers(tickers,
                          tiingo_api_key,
                          start_date=None,
                          end_date=None,
                          save_to='',
                          check_existing=True):
    """
    Persist all the available data for each of the ticker in ticker_list
    """

    n_tickers = len(tickers)
    bar = progressbar.ProgressBar(maxval=n_tickers,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ',
                                           progressbar.Percentage()])


    config = {}
    # To reuse the same HTTP Session across API calls (and have better performance), include a session key
    config['session'] = True
    config['api_key'] = tiingo_api_key
    # Initialize
    client = TiingoClient(config)
    result = dict()
    bar.start()

    if check_existing and save_to:
        result = pickle_load(save_to)

    for idx, ticker in enumerate(tickers):
        if check_existing and ticker not in result.keys():
            try:
                ticker_df = pdr.get_data_tiingo(ticker, start=start_date, end=end_date,
                                                pause=0.2, api_key=config['api_key'])
                result[ticker] = ticker_df
            except Exception as E:
                print(f"Unable to fetch data, exception: {E}")
                result[ticker] = None
        else:
            # TODO pull only latest needed data by checking last date
            pass
        bar.update(idx)

    bar.finish()
    if save_to:
        pickle_dump(result, save_to)

    return result



if __name__ == "__main__":
    api_key = myconfigs['fi.ini']['tiingo']['api']
    save_to_insider = '/Users/Christian.Avart/Dropbox/py4fi_data/insider_buying.csv'
    save_to_insider = ''
    insider_monkey_df = get_insider_df(n_pages=3, save_to=save_to_insider)
    # insider_monkey_df = pd.read_csv(save_to_insider)
    # insider_monkey_df['Date'] = insider_monkey_df['Date'].apply(parse)
    insider_monkey_df.head()

    save_to_return = '/Users/Christian.Avart/Dropbox/py4fi_data/insider_buying_return.csv'
    save_to_return = ''
    insider_purchase_return = get_insider_purchase_performance(insider_monkey_df,
                                                               api_key=api_key,
                                                               min_total_trigger=1e6,
                                                               length_in_days=180,
                                                               save_to=save_to_return)
    # insider_purchase_return = pd.read_csv(save_to_return)
    print(insider_purchase_return)
