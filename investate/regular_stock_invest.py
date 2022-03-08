"""
Function to compute the total return of a stock by taking into account both the stock value and the dividend yield
This is a baby function, rather use a good data source like Tiingo since there are more factors to take into account.

Example of use:

growth_series = get_total_return_from_monthly_data(start_date='1980-03-25', end_date='2021-03-01')
plt.plot(growth_series)
plt.show()

"""

from investate.quandl_data import *


def get_total_return_from_monthly_data(
    price_tick={'tick': 'MULTPL/SP500_REAL_PRICE_MONTH', 'data_cols': ['Value'],},
    dividend_tick={'tick': 'MULTPL/SP500_DIV_YIELD_MONTH', 'data_cols': ['Value'],},
    start_date='1910-01-01',
    end_date='2021-03-01',
    remove_begining=True,
):
    """Attempt at getting the full return of a stock if dividends are reinvested"""
    ticks_dicts = {'price': price_tick, 'dividends': dividend_tick}
    df = make_df_from_ticks(
        ticks_dicts=ticks_dicts, start_date=start_date, end_date=end_date
    )
    if remove_begining:
        begining_of_month_indices = [
            i for idx, i in enumerate(list(df.index)) if idx % 2 == 0
        ]
        df = df.drop(begining_of_month_indices)
    df['shift_price'] = df.price_Value.shift(1)
    growth_series = (
        df['dividends_Value'] / (12 * 100) + df['price_Value'] / df['shift_price']
    )
    return growth_series.iloc[1:]
