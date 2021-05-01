import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import quandl
import itertools
import os
from pathlib import Path

# get your quandl api key. Place a .txt file on your desktop with the api key in it,
# or alternatively place it anywhere and manualy replace the path below
path_to_key = os.path.expanduser('~/Desktop/quandl_api_key.txt')
api_key = Path(path_to_key).read_text()
api_key = api_key.replace('\n', '')
quandl.ApiConfig.api_key = api_key

ticks_dicts = {'btc': {'tick': 'BCHARTS/BITSTAMPUSD', 'data_cols': ['Close', 'Volume (BTC)']},
               'eth': {'tick': 'BITFINEX/ETHUSD', 'data_cols': ['Last']},
               'idx500': {'tick': 'MULTPL/SP500_REAL_PRICE_MONTH', 'data_cols': ['Value']},
               'gold': {'tick': 'WGC/GOLD_DAILY_USD', 'data_cols': ['Value']},
               'gas': {'tick': 'FRED/GASREGCOVW', 'data_cols': ['Value']},
               'cons_idx': {'tick': 'UMICH/SOC1', 'data_cols': ['Index']},
               'month_sav': {'tick': 'FRED/PSAVERT', 'data_cols': ['Value']},
               'yale_cons_idx': {'tick': 'YALE/US_CONF_INDEX_VAL_INST', 'data_cols': ['Index Value']},
               'cons_idx_infl': {'tick': 'RATEINF/CPI_USA', 'data_cols': ['Value']},
               'cons_conf_idx': {'tick': 'OECD/KEI_CSCICP02_USA_ST_M', 'data_cols': ['Value']},
               'yearly_us_rate': {'tick': 'NAHB/INTRATES', 'data_cols': ['Federal Funds Rate',
                                                                         'Freddie Mac Commitment Fixed Rate Mortgages',
                                                                         'Prime Rate']},
               'fed_for': {'tick': 'FRED/BASE', 'data_cols': ['Value']}}


def get_col_names_for_tick(tick='BCHARTS/BITSTAMPUSD'):
    """
    Return the columns available for the tick. Startdate is late by default to avoid getting much data
    """
    return quandl.get(tick, start_date=None).columns


def make_df_from_ticks(ticks_dicts=ticks_dicts,
                       start_date='2017-01-01',
                       end_date='2030-12-31',
                       verbose=False):
    """
    Make a df from the ticks in the ticks_list
    """

    df = pd.DataFrame()
    first = True

    for name, tick_dict in ticks_dicts.items():
        if verbose:
            print(f'\nGetting data for {name}')
        for data_col in tick_dict['data_cols']:
            try:
                if verbose:
                    print(f'{data_col}')
                tick_data = quandl.get(tick_dict['tick'], start_date=start_date, end_date=end_date)
                if first:
                    df[name + '_' + data_col] = tick_data[data_col]
                    first = False
                else:
                    new_df = pd.DataFrame()
                    new_df[name + '_' + data_col] = tick_data[data_col]
                    df = pd.concat([df, new_df], axis=1, sort=False)

            except Exception as E:
                pass
                #print(E, f'Available columns for {name}', tick_data.columns)

    # fill forward and backward the missing data
    df.fillna(method='ffill', axis=0, inplace=True)
    df.fillna(method='bfill', axis=0, inplace=True)

    return df


class divide_by_first:

    def __init__(self, date=None):
        self.date = date

    def fit_transform(self, series):
        if self.date:
            divisor = series.loc[self.date]
        else:
            divisor = series.iloc[0]
        series.apply(lambda x: x / divisor)
        return series.apply(lambda x: x / divisor)


def normalize_df(df, columns=None, method=divide_by_first):
    if columns is None:
        columns = df.columns
    scaler = method()
    df_norm = df.copy()
    for col in columns:
        # if the fit_transform works on a series
        try:
            df_norm[col] = scaler.fit_transform(df_norm[col])
        # otherwise, like standard scaler, turn everything into an array of array of single value
        except Exception as E:
            df_norm[col] = scaler.fit_transform(np.array(df_norm[col]).reshape(-1, 1))
    return df_norm


def moving_average(values, window_size, pad=True):
    values = iter(values)
    first_window = list(itertools.islice(values, window_size - 1))

    if pad:
        for i in range(window_size - 1):
            yield np.mean(first_window[:i + 1])
    for value in values:
        first_window.append(value)
        if len(first_window) == window_size:
            yield np.mean(first_window)
            first_window = first_window[1:]


def add_moving_average_col(df, col_name, window_size):
    df[f'{col_name}_ma{window_size}'] = list(moving_average(df[col_name], window_size=window_size, pad=True))
    df.columns = sorted(list(df.columns))
    return df


def get_total_return_from_monthly_data(price_tick={'tick': 'MULTPL/SP500_REAL_PRICE_MONTH', 'data_cols': ['Value']},
                                       dividend_tick={'tick': 'MULTPL/SP500_DIV_YIELD_MONTH', 'data_cols': ['Value']},
                                       start_date='1910-01-01',
                                       end_date='2021-03-01',
                                       remove_begining=True):
    ticks_dicts = {'price': price_tick, 'dividends': dividend_tick}
    df = make_df_from_ticks(ticks_dicts=ticks_dicts,
                            start_date=start_date,
                            end_date=end_date)
    if remove_begining:
        begining_of_month_indices = [i for idx, i in enumerate(list(df.index)) if idx % 2 == 0]
        df = df.drop(begining_of_month_indices)
    df['shift_price'] = df.price_Value.shift(1)
    growth_series = df['dividends_Value'] / (12 * 100) + df['price_Value'] / df['shift_price']
    return growth_series.iloc[1:]


def get_investment_growth(amount, growth_series):
    amount_per_months = [amount]
    for month_rate in growth_series:
        amount *= month_rate
        amount_per_months.append(amount)
    return amount_per_months


if __name__ == '__main__':

    growth_series = get_total_return_from_monthly_data(
        start_date='1980-03-25',
        end_date='2021-03-01')
    invest_over_time = get_investment_growth(100, growth_series)
    plt.plot(invest_over_time)
    plt.show()
