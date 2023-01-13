"""Proposals from tw"""

from functools import partial
from typing import Literal

from investate.data_apis import *

# TODO: Centralize all configs into one place that can be controlled by config file etc.
DFLT_TICKER = 'SPY'


def five_years_ago_yyyymmdd():
    return (datetime.datetime.now() - datetime.timedelta(days=5 * 365)).strftime(
        '%Y%m%d'
    )


def now_yyyymmdd():
    return datetime.datetime.now().strftime('%Y%m%d')


Frequency = Literal['daily', '1min', '5min', 'yearly']


def _ticker_to_path(
    ticker: str,
    *,
    subpath_template,
    frequency: Frequency = 'daily',
    root_dir=DFLT_SOURCE_DIR,
):
    return os.path.join(
        root_dir, subpath_template.format(ticker=ticker, frequency=frequency)
    )


CA_TICKER_TO_SUBPATH = partial(
    _ticker_to_path, frequency='daily', subpath_template='{ticker}_{frequency}.csv',
)

TW_TICKER_TO_SUBPATH = partial(
    _ticker_to_path, frequency='daily', subpath_template='{frequency}/{ticker}.csv',
)

DFLT_TICKER_TO_SUBPATH = CA_TICKER_TO_SUBPATH


def fetch_data_and_cache(
    ticker=DFLT_TICKER,
    start=None,
    end=None,
    *,
    ticker_to_path=DFLT_TICKER_TO_SUBPATH,
    fetch_func=pdr.get_data_tiingo,
    date_col_name='date',
    drop_duplicates=False,
    **fetch_func_kwargs,
):
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

    # TODO: Delete backcomp stuff when no longer needed
    _backcomp_stuff = {
        'append_to_path': fetch_func_kwargs.pop('append_to_path', None),
        'source': fetch_func_kwargs.pop('source', None),
    }
    if any(_backcomp_stuff.values()):
        ticker_to_path = _mk_append_to_path_ticker_to_path(**_backcomp_stuff)
    # --------------------------------------------------------------------------------

    # TODO: Revise logic here. There are many choices. Is this the one we want?
    #  See https://github.com/cavart28/investate/issues/1
    if start is None:
        start = five_years_ago_yyyymmdd()
    if end is None:
        end = now_yyyymmdd()

    # existing_tickers_and_freq_str, path_to_csv, ticker_and_freq_str = _get_path_to_csv(
    #     ticker, append_to_path, source
    # )

    path_to_csv = ticker_to_path(ticker)
    ts_start = normalize_to_utc_pd_timestamp(start)
    ts_end = normalize_to_utc_pd_timestamp(end)

    if os.path.isfile(path_to_csv):
        ticker_df = pd.read_csv(
            path_to_csv, parse_dates=['date'], date_parser=normalize_to_utc_pd_timestamp
        )

        ts_existing_start = ticker_df['date'].iloc[0]
        ts_existing_end = ticker_df['date'].iloc[-1]

        ts_new_end = max(ts_existing_end, ts_end)
        ts_new_start = min(ts_existing_start, ts_start)

        left_query = (ts_new_start, ts_existing_start)
        right_query = (ts_existing_end, ts_new_end)

        for i, query in enumerate([left_query, right_query]):
            if len(set(query)) == 2:
                ts_start, ts_end = query
                result_df = fetch_func(
                    ticker, start=ts_start, end=ts_end, **fetch_func_kwargs
                )

                result_df.reset_index(inplace=True)
                result_df['date'] = result_df[date_col_name].apply(
                    normalize_to_utc_pd_timestamp
                )

                if date_col_name != 'date':
                    result_df.drop(date_col_name, axis=1, inplace=True)
                # Remove the last row of result_df since the query returns inclusive upper bound
                if i == 0:
                    ticker_df = pd.concat(
                        objs=(result_df.iloc[:-1], ticker_df), ignore_index=True
                    )
                else:
                    ticker_df = pd.concat(
                        objs=(ticker_df, result_df.iloc[1:]), ignore_index=True
                    )
                ticker_df.reset_index(inplace=True, drop=True)

    else:
        ticker_df = fetch_func(ticker, start=start, end=end, **fetch_func_kwargs)
        ticker_df.reset_index(inplace=True)
        # standardise the name of the date column and its format
        ticker_df['date'] = ticker_df[date_col_name].apply(
            normalize_to_utc_pd_timestamp
        )
        if date_col_name != 'date':
            ticker_df.drop(date_col_name, axis=1, inplace=True)
    if drop_duplicates:
        ticker_df = ticker_df.drop_duplicates('date')
        ticker_df.reset_index(inplace=True, drop=True)

    ticker_df.to_csv(path_to_csv, index=False)
    return ticker_df.set_index('date', drop=False)


# Backcompatibility stuff:
# TODO: Delete backcomp stuff when no longer needed

allowed_suffix = ('_daily', '_1min', '_5min', '_yearly')

DFLT_APPEND_TO_PATH = '_daily'


def _append_to_path_ticker_to_path(ticker, append_to_path, source):
    assert append_to_path in allowed_suffix, (
        f'Your suffix must be in allowed_suffix,'
        f' either comply or extend allowed_suffix if a new one is warranted'
    )
    return os.path.join(source, f'{ticker}{append_to_path}.csv')


def _mk_append_to_path_ticker_to_path(append_to_path, source):
    append_to_path = append_to_path or DFLT_APPEND_TO_PATH
    source = source or DFLT_SOURCE_DIR
    return partial(
        _append_to_path_ticker_to_path, source=source, append_to_path=append_to_path,
    )
