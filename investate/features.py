"""Functions computing features"""

from investate.series_utils import parallel_sort
import numpy as np


def chunk_up_down_count(chunk, n_derivative=0):
    """Chunk count of ups and downs"""
    diff_chunk = np.diff(chunk, n_derivative)

    first = diff_chunk[0]
    n_up = 0
    for second in diff_chunk[1:]:
        if first <= second:
            n_up += 1
        first = second
    n_down = len(diff_chunk) - 1 - n_up

    return n_up, n_down


def get_aligned_ma(series, chunk_sizes, chk_funcs, pad_with=np.nan):
    """
    Convenience function to compute and align several moving averages of a series.
    Possibly should be replaced with pandas rolling method

    >>> series = range(10)
    >>> chunk_sizes = (2, 4, 6)
    >>> chk_funcs = [np.mean] * 3
    >>> a, b, c = get_aligned_ma(series, chunk_sizes, chk_funcs)
    >>> a
    [nan, nan, nan, nan, nan, 4.5, 5.5, 6.5, 7.5, 8.5]
    >>> b
    [nan, nan, nan, nan, nan, 3.5, 4.5, 5.5, 6.5, 7.5]
    >>> c
    [nan, nan, nan, nan, nan, 2.5, 3.5, 4.5, 5.5, 6.5]
    """

    sorted_chunks, sorted_funcs = parallel_sort([chunk_sizes, chk_funcs])
    largest_chunks = sorted_chunks[-1]
    n_chunks = len(series) - largest_chunks + 1

    series = list(series)
    series.reverse()

    all_stats_series = []

    for chk_size, chk_func in zip(sorted_chunks, sorted_funcs):
        stat_series = []
        for i in range(n_chunks):
            chunk = series[i : i + chk_size]
            stat_series.append(chk_func(chunk))
        stat_series.reverse()
        all_stats_series.append(stat_series)
    series.reverse()

    if pad_with is not None:
        all_stats_series = [
            [pad_with] * (largest_chunks - 1) + i for i in all_stats_series
        ]

    return all_stats_series


config_dict = {'Tiingo': {'close': 'close', 'open': 'open'}}


class Volatility:
    def __init__(self, df, data_origin='Tiingo'):
        self.col_names = config_dict[data_origin]
        self.df = df

    def up_down_dist(self, col='close'):
        col = self.col_names[col]
        series = self.df[col]
        growth = series.shift(1) / series > 1
        growth.apply(lambda x: int(x))
        trend_change = growth.shift(1) != growth
        groups = trend_change.cumsum()
        trends = self.df.groupby(groups)
