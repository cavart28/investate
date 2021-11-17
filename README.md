# Investate

A collection of tools to find the value over time of various investments.

"How much would I have if I invest every month $10 on a bank account at a rate of 5%"
Basic calculus offers a simple formula to answer the question above.
If more realistically, you invest a different amount every months, and the rate is changing over time,
there is no algebraic shortcut to get an answer. You can then use the function values_of_series_of_invest to get
an answer:

```python
from investate.series_utils import values_of_series_of_invest

values_of_series_of_invest(rate_between_period=[0.01, 0.005, 0.011], 
                           invest_values=[10, 12, 5])

27.292549999999995
```

Investate contains simple tools to backtest strategies. Below is an example basde on the standard 
crossing averages.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# We choose a series of value of an investment over time, eth_series, the value of Ethereum
# over time
import pandas as pd
eth_series = pd.read_csv('test_dfs/eth.csv')
print(eth_series)
```
![alt text](investate/.README_images/img.png)

![alt text33](investate/.README_images/img2.png)
![alt text333](.README_images/img2.png)
```python
# Then we set our moving average parameters, namely the size of windows (which we call chunks here) used for the rolling means
chk_size_1 = 10
chk_size_2 = 30

from investate.moving_average import get_comp_ma

# get_comp_ma returns a dictionary containing the aligned numpy series of the moving averages
# along with the original series appropriatelly cut off to be aligned with the shortest
stat_dict = get_comp_ma(eth_series, chk_size_1=chk_size_1, chk_size_2=chk_size_2)
stat_series_1, stat_series_2, cut_series = stat_dict['stat_series_1'], stat_dict['stat_series_2'], stat_dict[
    'cut_series']

# get the growth of the cut_series, i.e, the value over time of an investment of 1 dollar
from investate.series_utils import values_to_percent_growth

period_rate_A = values_to_percent_growth(cut_series)

# get the growth over time of the alternative investment, here we choose holding cash at 0% APR
period_rate_B = [0] * len(cut_series)

# get the function which determines the rebalance of the investments
from investate.backtesting_examples import invest_with_sma

invest_func = invest_with_sma(chk_size_1=chk_size_1, chk_size_2=chk_size_2)

# invest_with_sma applied to our series eth_series of 0/1 determining whether to invest in ethereum for each period
invest_period = np.array(list(invest_func(eth_series)))

# normalize invest_period to draw on a plot together with the investment
invest_period_for_plot = invest_period * np.max(cut_series)

# plot the ma's together
from investate.backtesting_examples import plot_mas

fig, ax = plot_mas(**stat_dict)

# add the invest/devest curve
ax.plot(invest_period[chk_size_2 - 1:], label='invest/devest', linewidth=0.3, linestyle='--')
plt.legend(loc=(1.05, 0.8))
plt.tight_layout()
plt.show()
```

```python

# compute the values of both investments ethereum/saving over time and plot them
# fees_func is set to None, meaning that we assume there is no fee to transwer from A to B and B to A

from investate.series_utils import investment_over_period

val_A, val_B = investment_over_period(period_rates_A=period_rate_A,
                                      period_rates_B=period_rate_B,
                                      fees_func_AB=None,
                                      period_end_balance=invest_period,
                                      initial_investment_A=1,
                                      initial_investment_B=0)

# Plot the investements A and B together with the original series
plt.plot(val_A)
plt.plot(val_B)
plt.show()
plt.plot(cut_series)
plt.show()
```

```python
# find the total of the investment
total = np.array(val_A) + np.array(val_B)

# print the total return of the original series and of the investment strategy
print(cut_series[-1] / cut_series[0], total[-1])
```