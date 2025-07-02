"""Functions computing features"""

from investate.series_utils import parallel_sort, values_to_percent_growth
import numpy as np
from itertools import islice
from collections import deque


def chunker(iterable, chk_size, chk_step=1):
    """
    >>> list(chunker(range(10), chk_size=2))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]

    >>> # Note that only FULL chunks are returned
    >>> list(chunker(range(9), chk_size=2))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]

    >>> list(chunker(range(9), chk_size=2, chk_step=3))
    [(0, 1), (3, 4), (6, 7)]
    """

    iterable = iter(iterable)
    initial = list(islice(iterable, chk_size))
    d = deque(
        initial, maxlen=int(chk_size)
    )  # applying int to avoid an issue with in64 being rejected by deque

    if len(d) == chk_size:
        yield tuple(d)
    to_add = list(islice(iterable, chk_step))
    d.extend(to_add)

    while len(to_add) == chk_step:
        yield tuple(d)
        to_add = list(islice(iterable, chk_step))
        d.extend(to_add)


def moving_stats(series, chk_size, chk_step=1, chk_func=np.mean, pad=None):
    """
    Compute the moving averages of the series (or moving stats more generally), where winsize is the size of the
    windows and win_func the function computing the stat for each of them.
    Note that we could have included a step but this is not terribly useful in financial application and the step
    can always be applied "afterwards" by selecting only some of the averages, the computational cost being rather
    small for financial series

    :param series: list of floats
    :param chk_size: int, the size of the window
    :param chk_step: int, the step from one window to the next window
    :param chk_func: callable, a function compute a stat for each of the windows
    :return: list of stats over each of the window


    >>> series = range(10)
    >>> moving_stats(series, chk_size=2, chk_func=np.mean)
    [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]

    The size of the series outputed with the default step of size 1 is always len(series) - chk_size + 1

    >>> chk_size, series_length = 12, 100
    >>> series = range(series_length)
    >>> assert len(moving_stats(series, chk_size=chk_size)) == series_length - chk_size + 1, 'something is wrong!'

    One can compute more complicated moving averages by using various win_func

    >>> series = range(10)
    >>> chk_size = 2
    >>> chk_func = lambda x: np.mean(np.array(x) * np.array([0.1] * chk_size))
    >>> moving_stats(series, chk_size=chk_size, chk_func=chk_func)
    [0.05, 0.15000000000000002, 0.25, 0.35000000000000003, 0.45, 0.55, 0.6500000000000001, 0.75, 0.8500000000000001]
    """

    chunks = chunker(series, chk_size, chk_step)
    stats = list(map(chk_func, chunks))
    if pad is not None:
        stats = [pad] * (chk_size - 1) + stats
    return stats


def window_up_down_count(window, n_derivative=0):
    """window count of ups and downs"""
    diff_chunk = np.diff(window, n_derivative)

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
    Possibly should be replaced with pandas rolling method.
    General and convenient but in most case much faster case specific versions can be coded.
    (for example when chk_funcs is the mean, std, sorted, max...)

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


def sector_normalized_growth(ticker_values,
                             comp_tickers_list_values,
                             weights=None):
    """

    Here the comparative tickers grow at the same rate, so the relative growth is 0 for each period

    >>> sector_normalized_growth(ticker_values=[1, 2, 3],
                                 comp_tickers_list_values=[[1, 2, 3], [1, 2, 3]],
                                 weights=[1, 1])
    array([0., 0.])


    If now one of the equity has a lesser growth (or a loss here), the difference is now positive

    >>> sector_normalized_growth(ticker_values=[1, 2, 3],
                                 comp_tickers_list_values=[[1, 0.8, 0.9], [1, 2, 3]],
                                 weights=[1, 1])
    array([0.6   , 0.1875])


    Changing the weights will affect the realtive effect of each of the comparative equities

    >>> sector_normalized_growth(ticker_values=[1, 2, 3],
                                 comp_tickers_list_values=[[1, 0.8, 0.9], [1, 2, 3]],
                                 weights=[2, 1])
    array([0.8 , 0.25])

    """

    if weights is None:
        weights = np.array([1] * len(comp_tickers_list_values))

    comp_values_growth = np.array([values_to_percent_growth(values) for values in comp_tickers_list_values])
    weighted_comp_values_growth = (comp_values_growth.T * weights).T
    comp_values_growth_mean = np.sum(weighted_comp_values_growth, axis=0) / np.sum(weights)
    normalized_ticker_values = values_to_percent_growth(ticker_values)

    return normalized_ticker_values - comp_values_growth_mean


def time_up_time_down(series):
    """
    Return the number of times a series goes up and the number of time a series goes down (strictly)

    :param series: list of float
    :return: a pair of integers

    >>> time_up_time_down([1,2,3,2])
    (2, 1)
    >>> time_up_time_down([1, 1, 1])
    (3, 0)
    """

    diff = np.diff(series)
    pos = np.sum(diff >= 0)
    neg = np.sum(diff < 0)
    return pos, neg


def distribution_growth(series, bins=[-0.5, -0.2, -0.1, 0, 0.01, 0.2, 0.5]):
    """
    >>> frq, edges = distribution_growth([1, 1.1, 1.2, 1.15])
    >>> frq, edges
    (array([0, 0, 1, 0, 2, 0]), array([-0.5 , -0.2 , -0.1 ,  0.  ,  0.01,  0.2 ,  0.5 ]))

    """
    growth = values_to_percent_growth(series)
    return np.histogram(growth, bins=bins)


def series_growth(pd_series):
    """
    Compute the periods growth for a series of values, i.e. the percentage gain from one period to the next. The last one
    will always be NaN since no next one is available.

    :param series: a pandas series
    :return: a pandas series
    """
    return (pd_series / pd_series.shift(1) - 1).shift(-1)

