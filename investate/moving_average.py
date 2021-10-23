import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import product


def moving_average(x, win):
    if isinstance(win, (int, np.integer)):
        window = np.ones(win)
        len_win = win
    else:
        window = win
        len_win = len(window)
    return np.convolve(x, window, 'valid') / len_win


def get_comp_ma(series, ma_1, ma_2, plot=False):
    # make ma_1 is always the smallest
    both = [ma_1, ma_2]
    both = np.sort(both)
    ma_1, ma_2 = both
    ma_series_1 = moving_average(series, ma_1)
    ma_series_2 = moving_average(series, ma_2)
    offset = np.abs(ma_2 - ma_1)
    cut_ma_series_1 = ma_series_1[offset:]
    cut_ma_series_2 = ma_series_2

    if plot:
        plt.plot(cut_ma_series_1, label=f'ma_{ma_1}')
        plt.plot(cut_ma_series_2, label=f'ma_{ma_2}')
        plt.plot(series[ma_2:], label=f'series')
        plt.legend()

    return np.array(cut_ma_series_1), np.array(cut_ma_series_2), np.array(series[ma_2 - 1:])


def moving_average_grid(series, ma_range=range(10)):
    mat = np.zeros((len(ma_range), len(ma_range)))
    means = []
    for ma in ma_range:
        means.append(np.mean(series[-ma:]))
    for i, j in product(ma_range, ma_range):
        if i < j:
            mat[i, j] = means[i] - means[j]
    return mat


def plot_ma_grid(series, n_days):
    mat = moving_average_grid(series, ma_range=range(n_days))
    sns.set_theme(style="white")

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(6, 6))
    # remove the bottom of the matrix in the plot
    mask = np.tril(np.ones_like(mat, dtype=bool))

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(mat, mask=mask, vmax=np.max(mat), vmin=np.min(mat), center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})
    plt.plot()
