import numpy as np


def values_of_series_of_invest(invest_amounts,
                               rate_between_amounts,
                               final_only=True,
                               invest_at_begining_of_period=False):
    """
    Total values after investing each of the values in invest_values, the running total increasing
    by the percentage in rate_between_values from one investment to the next.
    By default invest_at_begining_of_period is set to False meaning that each investment is made
    at the begining of the period and thus is not subject to the period growth.

    :param: invest_values, an iterable of invested values
    :param: rate_between_values, an iterable of rate of growth for the periods from one
                                 investment to the next
    :param: invest_at_begining_of_period, boolean, whether to invest at the begining of a period
            or the end.

    >>> values_of_series_of_invest([1, 1], [0, 0])
    2
    >>> # final_only controls whether to get the intermediate values
    >>> values_of_series_of_invest([1, 1], [0, 0], final_only=False)
    [1, 2]
    >>> # the first rate is not used by default, since the amounts are invested at the END of the period
    >>> values_of_series_of_invest([1, 1], [0.05, 0], final_only=False)
    [1.0, 2.0]
    >>> # this can be changed however, by setting invest_at_begining_of_period to True
    >>> values_of_series_of_invest([1, 1], [0.05, 0], invest_at_begining_of_period=True, final_only=False)
    [1.05, 2.05]
    >>> values_of_series_of_invest([1, 1], [0.05, 0.08], invest_at_begining_of_period=True, final_only=False)
    [1.05, 2.1340000000000003]

    # it can easily be used to get total invested value after several regular investments
    >>> n_years = 10
    >>> rate = 0.08
    >>> yearly_investment = 100
    >>> values_of_series_of_invest([yearly_investment] * n_years, [rate] * n_years)
    1448.656246590984

    # another application is to get the historical growth of a stock from one year to the next
    # to evaluate the total value of a series of investments

    """

    if invest_at_begining_of_period:
        total = invest_amounts.pop(0) * (1 + rate_between_amounts.pop(0))
        value_over_time = [total]
    else:
        total = 0
        value_over_time = []

    for invest, rate in zip(invest_amounts, rate_between_amounts):
        total = total * (1 + rate) + invest
        value_over_time.append(total)

    if final_only:
        return total
    else:
        return value_over_time


def total_of_regular_investment(reg_invest_value, rate, n_periods):
    """
    A special case of total_of_series_of_invest, when the investements are constant and the rate
    remains constant. Uses math formula instead of recursion. Not super useful except may be to
    keep track of the formula for other usage.

    >>> total_of_regular_investment(10, 0, 5)
    50
    # the investment is applied at the END of the period and thus does not benefit from its growth
    >>> total_of_regular_investment(10, 0.01, 1)
    10.0
    >>> total_of_regular_investment(10, 0.01, 2)
    20.099999999999987
    >>> total_of_regular_investment(10, 0.01, 5)
    51.0100501000001
    """

    if rate == 0:
        return reg_invest_value * n_periods
    else:
        factor = 1 + rate
        return reg_invest_value + reg_invest_value * (factor - factor ** n_periods) / (1 - factor)



def values_to_percent_growth(values):
    """
    Turn a series of values into a series giving the growth from one period to the next
    :param values: a list of floats
    :return: another list, of length one less than values

    >>> rate = 0.05
    >>> values = np.array([(1 + rate) ** i  for i in range(5)])
    >>> values_to_percent_growth(values)
    array([0.05, 0.05, 0.05, 0.05])
    """

    values = np.array(values)
    shifted_values = np.roll(values, shift=-1)
    period_growth = shifted_values / values
    return period_growth[:-1] - 1


def relative_weight(A, B):
    return A / (A + B)


def rebalance_A_to_B(A, B, target_relative_weight, transfer_fee):
    """
    We want to solve:
    (A - transfer) / (A - transfer + B + transfer * (1 - transfer_fee)) = target_relative_weight
    which can be solved into:
    transfer = (A - target_relative_weight * (A + B)) / (1 - target_relative_weight * transfer_fee)

    :param A: float, value of A
    :param B: float, value of B
    :param target_relative_weight: what A / (A + B) should be after rebalancing
    :param transfer_fee: a percentage taken from the transfer of value from A to B
    :return: the amount to transfer from A to B to achieve the target_relative_weight


    >>> # A and B are already balanced, nothing must be taken fomr A
    >>> rebalance_A_to_B(10, 10, 0.5, 0)
    0.0
    >>> # for A to be 25% of the total, we need to move 5 unit from A to B (assuming no transfer fee)
    >>> rebalance_A_to_B(10, 10, 0.25, 0)
    5.0
    >>> # on the other hand, we need to GIVE to A to make A 0.75% of the total (still assuming no transfer fee)
    >>> rebalance_A_to_B(10, 10, 0.75, 0)
    -5.0
    >>> # example including a transfer fee
    >>> rebalance_A_to_B(10, 10, 0.25, 0.01)
    5.012531328320802
    """
    return (A - target_relative_weight * (A + B)) / (1 - target_relative_weight * transfer_fee)


def investment_over_period(period_rates_A,
                           period_rates_B,
                           fees_func_AB,
                           period_end_balance,
                           initial_investment_A=1,
                           initial_investment_B=0):
    """
    It is assumed that the initial investment is 1 unit in value and that it can be transferred between two investments A and B
    following the fees_func_AB. This function is really two in one: one for positive values (corresponding to transfers
    from A to B) and one for negative values (corresponding to transfer from B to A). The fees_func_AB is assumed to be
    a function of the total values invested in A and the total value invested in B. (reflecting a possible discount when the
    investments are large). In reality the fee is usually also a function of the transfer amount but this is more difficult
    to capture since the equation solved in rebalance_A_to_B become functional. To generalize rebalance_A_to_B, one would
    probably need to use some form of iterative approximation. I intend to trade with Robinhood, which has no fee, which is
    one more reason to take this simplified approach.
    The period_end_balance represents the desired "balance" between investment A and B at the END of the period.

    >>> period_rates_A = [0.05, 0.05, 0, 0]
    >>> period_rates_B = [0, 0, 0.05, 0.05]
    >>> fees_func_AB = lambda x, y: 0 # no fees
    >>> period_end_balance = [ 1, 0, 0, 0]
    >>> initial_investment_A = 1
    >>> initial_investment_B = 0
    >>> investment_over_period(period_rates_A, period_rates_B, fees_func_AB, period_end_balance, initial_investment_A, initial_investment_B)
    (0.0, 1.2155062500000002)
    """

    total_A = initial_investment_A
    total_B = initial_investment_B

    for rate_A, rate_B, end_balance in zip(period_rates_A, period_rates_B, period_end_balance):
        # each investment grew during the period
        total_A = total_A * (1 + rate_A)
        total_B = total_B * (1 + rate_B)
        # we want to rebalance from A to B (or from B to A)
        A_to_B = rebalance_A_to_B(total_A, total_B, end_balance, transfer_fee=fees_func_AB(total_A, total_B))
        total_A -= A_to_B
        total_B += A_to_B
    return total_A, total_B


if __name__ == "__main__":
    period_rates_A = [0.05, 0.05, 0, 0]
    period_rates_B = [0, 0, 0.05, 0.05]
    fees_func_AB = lambda x, y: 0  # no fees
    period_end_balance = [1, 0, 0, 0]
    initial_investment_A = 1
    initial_investment_B = 0
    investment_over_period(period_rates_A, period_rates_B,
                           fees_func_AB, period_end_balance,
                           initial_investment_A, initial_investment_B)