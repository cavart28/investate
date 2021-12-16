"""
Functions to compute moving average of series and more in general, stats on rolling windows

Example of use:

plot_mas(**get_comp_ma(series, chk_size_1=10, chk_size_2=20, chk_step=1, chk_func_1=np.mean, chk_func_2=np.mean))

To visually test plot_mas:
series = np.concatenate((np.array([100]), np.ones(30), np.ones(30) * 2))
plot_mas(**get_comp_ma(series, chk_size_1=10, chk_size_2=20, chk_step=1, chk_func_1=np.mean, chk_func_2=np.mean))

"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import product, islice
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


def moving_stats(series, chk_size, chk_step=1, chk_func=np.mean):
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
    >>> list(moving_stats(series, chk_size=2, chk_func=np.mean))
    [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]

    The size of the series outputed with the default step of size 1 is always len(series) - chk_size + 1

    >>> chk_size, series_length = 12, 100
    >>> series = range(series_length)
    >>> assert len(list(moving_stats(series, chk_size=chk_size))) == series_length - chk_size + 1, 'something is wrong!'

    One can compute more complicated moving averages by using various win_func

    >>> series = range(10)
    >>> chk_size = 2
    >>> chk_func = lambda x: np.mean(np.array(x) * np.array([0.1] * chk_size))
    >>> list(moving_stats(series, chk_size=chk_size, chk_func=chk_func))
    [0.05, 0.15000000000000002, 0.25, 0.35000000000000003, 0.45, 0.55, 0.6500000000000001, 0.75, 0.8500000000000001]
    """

    chunks = chunker(series, chk_size, chk_step)
    return map(chk_func, chunks)


def get_comp_ma(
    series, chk_size_1, chk_size_2, chk_step=1, chk_func_1=np.mean, chk_func_2=np.mean,
):
    """
    Convenience function to compute and align the moving average of a series
    """

    # make chk_size_1 is always the smallest
    chk_size_1, chk_size_2 = np.sort([chk_size_1, chk_size_2])
    offset = chk_size_2 - chk_size_1
    series = list(series)
    stat_series_1 = list(
        moving_stats(
            series[offset:], chk_size_1, chk_step=chk_step, chk_func=chk_func_1
        )
    )
    stat_series_2 = list(
        moving_stats(series, chk_size_2, chk_step=chk_step, chk_func=chk_func_2)
    )

    return {
        'stat_series_1': np.array(stat_series_1),
        'stat_series_2': np.array(stat_series_2),
        'cut_series': np.array(series[chk_size_2 - 1 :]),
        'chk_size_1': chk_size_1,
        'chk_size_2': chk_size_2,
    }


def plot_mas(stat_series_1, stat_series_2, cut_series, chk_size_1, chk_size_2):
    """
    Plot two moving averages on a single plot
    """

    fig, ax = plt.subplots(nrows=1, ncols=1)

    ax.plot(stat_series_1, label=f'ma_{chk_size_1}', linewidth=0.5)
    ax.plot(stat_series_2, label=f'ma_{chk_size_2}', linewidth=0.5)
    ax.plot(cut_series[:], label=f'series', linewidth=0.8)
    ax.legend()

    return fig, ax
