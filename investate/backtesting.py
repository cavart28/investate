from investate.moving_average import *
from investate.quandl_data import *
from investate.series_utils import investment_over_period, values_to_percent_growth


def invest_with_sma(ma_1, ma_2, thres_invest, thresh_devest):
    # ensure ma_2 is  the largest
    both = [ma_1, ma_2]
    np.sort(both)
    ma_1, ma_2 = both

    def invest_func(series):
        ma_dict = get_comp_ma(series, ma_1=ma_1, ma_2=ma_2)
        cut_ma_series_1, cut_ma_series_2 = ma_dict['ma_series_1'], ma_dict['ma_series_2']
        diff_ma_series = cut_ma_series_1 - cut_ma_series_2
        # return 0 until we have enough data to compute the largest window needed
        for i in range(ma_2 - 1):
            yield 1
        for i in diff_ma_series:
            if i > thres_invest:
                yield 1
            if i < thresh_devest:
                yield 0

    return invest_func


if __name__ == "__main__":
    from py2store import myconfigs

    # api_key = myconfigs['fi.ini']['quandl']['api']
    # quandl.ApiConfig.api_key = api_key

    # df = make_df_from_ticks(api_key=api_key,
    #                         ticks_dicts={'eth': {'tick': 'BITFINEX/ETHUSD', 'data_cols': ['Last']}})
    # df.to_csv('/Users/Christian.Avart/Desktop/temp_df.csv')

    df = pd.read_csv('/Users/Christian.Avart/Desktop/temp_df.csv')
    eth_series = list(df['eth_Last'][-500:])

    ma_1 = 40
    ma_2 = 10
    ma_dict = get_comp_ma(eth_series, ma_1=ma_1, ma_2=ma_2)
    ma_series_1, ma_series_2, cut_series = ma_dict['ma_series_1'], ma_dict['ma_series_2'], ma_dict['cut_series']
    invest_func = invest_with_sma(ma_1=ma_1, ma_2=ma_2, thres_invest=0, thresh_devest=0)
    invest_period = np.array(list(invest_func(eth_series)))
    invest_period_for_plot = invest_period * np.max(cut_series)
    # fig, ax = plot_mas(**ma_dict)
    # ax.plot(invest_period[ma_2-1:], label='invest/devest', linewidth=0.3, linestyle='--')
    # plt.legend(loc=(1.05, 0.8))
    # plt.tight_layout()
    # plt.show()

    period_rate_A = values_to_percent_growth(cut_series)
    period_rate_B = [0] * len(cut_series)

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

    total = np.array(val_A) + np.array(val_B)
    print(cut_series[-1]/cut_series[0], total[-1])
