import matplotlib.pyplot as plt
import itertools
from investate.quandl_data import *


def moving_average(values, window_size, pad=True):
    values = iter(values)
    first_window = list(itertools.islice(values, window_size - 1))

    if pad:
        for i in range(window_size - 1):
            yield np.mean(first_window[:i + 1])
    for value in values:
        first_window.append(value)
        if len(first_window) == window_size:
            yield np.mean(first_window)
            first_window = first_window[1:]


def add_moving_average_col(df, col_name, window_size):
    df[f'{col_name}_ma{window_size}'] = list(moving_average(df[col_name], window_size=window_size, pad=True))
    df.columns = sorted(list(df.columns))
    return df


def get_total_return_from_monthly_data(price_tick={'tick': 'MULTPL/SP500_REAL_PRICE_MONTH', 'data_cols': ['Value']},
                                       dividend_tick={'tick': 'MULTPL/SP500_DIV_YIELD_MONTH', 'data_cols': ['Value']},
                                       start_date='1910-01-01',
                                       end_date='2021-03-01',
                                       remove_begining=True):
    ticks_dicts = {'price': price_tick, 'dividends': dividend_tick}
    df = make_df_from_ticks(ticks_dicts=ticks_dicts,
                            start_date=start_date,
                            end_date=end_date)
    if remove_begining:
        begining_of_month_indices = [i for idx, i in enumerate(list(df.index)) if idx % 2 == 0]
        df = df.drop(begining_of_month_indices)
    df['shift_price'] = df.price_Value.shift(1)
    growth_series = df['dividends_Value'] / (12 * 100) + df['price_Value'] / df['shift_price']
    return growth_series.iloc[1:]


def get_investment_growth(amount, growth_series):
    amount_per_months = [amount]
    for month_rate in growth_series:
        amount *= month_rate
        amount_per_months.append(amount)
    return amount_per_months


if __name__ == '__main__':

    growth_series = get_total_return_from_monthly_data(
        start_date='1980-03-25',
        end_date='2021-03-01')
    invest_over_time = get_investment_growth(100, growth_series)
    plt.plot(invest_over_time)
    plt.show()
