"""Functions computing features"""

from investate.series_utils import parallel_sort
import numpy as np

def get_aligned_ma(
        series,
        chunk_sizes,
        chk_funcs,
        pad_with=np.nan):
    """
    Convenience function to compute and align several moving averages of a series

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
            chunk = series[i: i + chk_size]
            stat_series.append(chk_func(chunk))
        stat_series.reverse()
        all_stats_series.append(stat_series)
    series.reverse()

    if pad_with is not None:
        all_stats_series = [[pad_with] * (largest_chunks - 1) + i for i in all_stats_series]

    return all_stats_series
