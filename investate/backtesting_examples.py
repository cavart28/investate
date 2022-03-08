"""
Tools to backtest simple investing strategies


 Example of use, where ethseries is the series of daily values of ethereum

    # choose some moving average parameters
    chk_size_1 = 10
    chk_size_2 = 30

    # get the moving averages and "cut series", the original series aligned with the first of the longest moving average
    stat_dict = get_comp_ma(eth_series, chk_size_1=chk_size_1, chk_size_2=chk_size_2)
    stat_series_1, stat_series_2, cut_series = stat_dict['stat_series_1'], stat_dict['stat_series_2'], stat_dict['cut_series']

    # get the growth of the cut_series, i.e, the value over time of an investment of 1 dollar
    period_rate_A = values_to_percent_growth(cut_series)

    # get the growth over time of the alternative investment: saving at 0% APR
    period_rate_B = [0] * len(cut_series)

    # get the function which determines the rebalance of the investments
    invest_func = invest_with_sma(chk_size_1=chk_size_1, chk_size_2=chk_size_2)

    # get a series of 0/1 determining whether to invest in ethereum for each period
    invest_period = np.array(list(invest_func(eth_series)))

    # normalize invest_period to draw on a plot together with the investment
    invest_period_for_plot = invest_period * np.max(cut_series)

    # plot the ma's together
    fig, ax = plot_mas(**stat_dict)
    # add the invest/devest curve
    ax.plot(invest_period[chk_size_2-1:], label='invest/devest', linewidth=0.3, linestyle='--')
    plt.legend(loc=(1.05, 0.8))
    plt.tight_layout()
    plt.show()

    # compute the values of both investments ethereum/saving over time and plot them
    val_A, val_B = investment_over_period(period_rates_A=period_rate_A,
                                          period_rates_B=period_rate_B,
                                          fees_func_AB=None,
                                          period_end_balance=invest_period,
                                          initial_investment_A=1,
                                          initial_investment_B=0)

    plt.plot(val_A)
    plt.plot(val_B)
    plt.show()
    plt.plot(cut_series)
    plt.show()

    # find the total of the investment
    total = np.array(val_A) + np.array(val_B)
    # print the total return of the original series and of the investment strategy
    print(cut_series[-1] / cut_series[0], total[-1])
"""

from investate.moving_average import *
from investate.quandl_data import *
from investate.series_utils import (
    investment_over_period,
    values_to_percent_growth,
)


# ---------------------------------------------SMA----------------------------------------------------------------------


def invest_with_sma(chk_size_1, chk_size_2, thres_invest=0.5, thresh_devest=0.5):
    """
    Create a function/strategy which given a series output another series of 0 and 1's where 1 means invest
    and 0 means devest.

    """

    def invest_func(series):

        ma_dict = get_comp_ma(
            series,
            chk_size_1,
            chk_size_2,
            chk_step=1,
            chk_func_1=np.mean,
            chk_func_2=np.mean,
        )
        cut_stat_series_1, cut_stat_series_2 = (
            ma_dict['stat_series_1'],
            ma_dict['stat_series_2'],
        )
        diff_ma_series = cut_stat_series_1 - cut_stat_series_2
        # return 1 until we have enough data to compute the largest window needed
        for i in range(chk_size_2 - 1):
            yield 1
        for i in diff_ma_series:
            if i > thres_invest:
                yield 1
            if i < thresh_devest:
                yield 0

    return invest_func


def parameter_grid_search(series, max_chk_size):
    """
    Quick function to visualize the relative benefit of each pair of ma values
    """
    mat = np.zeros((max_chk_size, max_chk_size))
    chk_sizes = range(1, max_chk_size)
    all_return = []

    for (chk_size_1, chk_size_2) in product(chk_sizes, chk_sizes):
        if chk_size_2 > chk_size_1:
            stat_dict = get_comp_ma(
                series, chk_size_1=chk_size_1, chk_size_2=chk_size_2
            )
            stat_series_1, stat_series_2, cut_series = (
                stat_dict['stat_series_1'],
                stat_dict['stat_series_2'],
                stat_dict['cut_series'],
            )
            invest_func = invest_with_sma(chk_size_1=chk_size_1, chk_size_2=chk_size_2)
            invest_period = np.array(list(invest_func(series)))

            period_rate_A = values_to_percent_growth(cut_series)
            period_rate_B = [0] * len(cut_series)

            val_A, val_B = investment_over_period(
                period_rates_A=period_rate_A,
                period_rates_B=period_rate_B,
                fees_func_AB=None,
                period_end_balance=invest_period,
                initial_investment_A=1,
                initial_investment_B=0,
            )

            total = np.array(val_A) + np.array(val_B)
            mat[chk_size_1, chk_size_2] = total[-1]
            all_return.append(cut_series[-1] / cut_series[0])
    return np.mean(all_return), mat[1:, 1:]


def plot_mat(mat):
    """
    Dirty little function to plot and compare the return for simple moving average strategies
    """
    sns.set_theme(style='white')

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(6, 6))
    # remove the bottom of the matrix in the plot
    mask = np.tril(np.ones_like(mat, dtype=bool))

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(
        mat,
        mask=mask,
        vmax=np.max(mat),
        vmin=np.min(mat),
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={'shrink': 0.5},
    )
    plt.plot()
    plt.show()
