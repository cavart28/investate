import pandas as pd
from moving_average import *
from investate.investate.quandl_data import *

def invest_with_sma(ma_1, ma_2, thres_invest, thresh_devest):
    # ensure ma_2 si the largest
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
    invest_period = np.array(list(invest_func(eth_series))) * np.max(cut_series)
    fig, ax = plot_mas(**ma_dict)
    ax.plot(invest_period[ma_2-1:], label='invest/devest', linewidth=0.3, linestyle='--')
    plt.legend(loc=(1.05, 0.8))
    plt.tight_layout()
    plt.show()


