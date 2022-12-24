"""
Functions to compute moving average of series and more in general, stats on rolling windows

Example of use:

plot_mas(**get_comp_ma(series, chk_size_1=10, chk_size_2=20, chk_step=1, chk_func_1=np.mean, chk_func_2=np.mean))

To visually test plot_mas:
series = np.concatenate((np.array([100]), np.ones(30), np.ones(30) * 2))
plot_mas(**get_comp_ma(series, chk_size_1=10, chk_size_2=20, chk_step=1, chk_func_1=np.mean, chk_func_2=np.mean))

"""
import numpy as np
from investate.features import moving_stats
import matplotlib.pyplot as plt
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
