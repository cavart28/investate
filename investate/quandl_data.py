"""
Utils to get stock data from Quandl. Was inspired by a naive view on financial data and not really
appropriate for most usage. For example some data are daily and some are monthly, no effort was made at merging them
The only possible purpose is to easily get data for several stocks into one pandas df.
"""

import quandl
import numpy as np
import pandas as pd


ticks_dicts = {
    'btc': {'tick': 'BCHARTS/BITSTAMPUSD', 'data_cols': ['Close', 'Volume (BTC)'],},
    'eth': {'tick': 'BITFINEX/ETHUSD', 'data_cols': ['Last']},
    'idx500': {'tick': 'MULTPL/SP500_REAL_PRICE_MONTH', 'data_cols': ['Value'],},
    'gold': {'tick': 'WGC/GOLD_DAILY_USD', 'data_cols': ['Value']},
    'gas': {'tick': 'FRED/GASREGCOVW', 'data_cols': ['Value']},
    'cons_idx': {'tick': 'UMICH/SOC1', 'data_cols': ['Index']},
    'month_sav': {'tick': 'FRED/PSAVERT', 'data_cols': ['Value']},
    'yale_cons_idx': {
        'tick': 'YALE/US_CONF_INDEX_VAL_INST',
        'data_cols': ['Index Value'],
    },
    'cons_idx_infl': {'tick': 'RATEINF/CPI_USA', 'data_cols': ['Value']},
    'cons_conf_idx': {'tick': 'OECD/KEI_CSCICP02_USA_ST_M', 'data_cols': ['Value'],},
    'yearly_us_rate': {
        'tick': 'NAHB/INTRATES',
        'data_cols': [
            'Federal Funds Rate',
            'Freddie Mac Commitment Fixed Rate Mortgages',
            'Prime Rate',
        ],
    },
    'fed_for': {'tick': 'FRED/BASE', 'data_cols': ['Value']},
}


def get_col_names_for_tick(tick='BCHARTS/BITSTAMPUSD'):
    """
    Return the columns available for the tick. Startdate is late by default to avoid getting much data
    """
    return quandl.get(tick, start_date=None).columns


def make_df_from_ticks(
    api_key,
    ticks_dicts=ticks_dicts,
    start_date='2017-01-01',
    end_date='2030-12-31',
    verbose=False,
):
    """
    Make a df from the ticks in the ticks_list
    """

    quandl.ApiConfig.api_key = api_key
    df = pd.DataFrame()
    first = True

    for name, tick_dict in ticks_dicts.items():
        if verbose:
            print(f'\nGetting data for {name}')
        for data_col in tick_dict['data_cols']:
            try:
                if verbose:
                    print(f'{data_col}')
                tick_data = quandl.get(
                    tick_dict['tick'], start_date=start_date, end_date=end_date
                )
                if first:
                    df[name + '_' + data_col] = tick_data[data_col]
                    first = False
                else:
                    new_df = pd.DataFrame()
                    new_df[name + '_' + data_col] = tick_data[data_col]
                    df = pd.concat([df, new_df], axis=1, sort=False)

            except Exception as E:
                print(E, f'Available columns for {name}', tick_data.columns)

    # fill forward and backward the missing data
    df.fillna(method='ffill', axis=0, inplace=True)
    df.fillna(method='bfill', axis=0, inplace=True)

    return df


class divide_by_first:
    """
    Get the period growths for an investment whose values over time are given in a series
    """

    def __init__(self, date=None):
        self.date = date

    def fit_transform(self, series):
        """Get first term and divide all by first"""
        if self.date:
            divisor = series.loc[self.date]
        else:
            divisor = series.iloc[0]
        series.apply(lambda x: x / divisor)
        return series.apply(lambda x: x / divisor)


def normalize_df(df, columns=None, method=divide_by_first):
    """
    Normalize the columns of a dataframe
    """
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
