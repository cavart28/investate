"""
Tools to find the value over time of various investments, mainly to compare with real estate investment

Example of use:

from investate.real_estate_vs_stock import house_investment

equity, monthly_income = house_investment(mortg_rate=0.0265,
                                          down_payment_perc=0.1,
                                          house_cost=240000,
                                          tax=6000,
                                          insurance=4000,
                                          repair=6000,
                                          estate_rate=0.03,
                                          mortgage_n_years=15,
                                          n_years_after_pay_off=10,
                                          monthly_rental_income=7500,
                                          percentage_rented=0.5,
                                          inflation_rate=0.02,
                                          income_tax=0.36,
                                          management_fees_rate=0.22,
                                          plot=True)
"""

import matplotlib.pyplot as plt
from investate.series_utils import *


def compute_mortg_principal(
    loan_rate=0.04, loan_amount=1000, years_to_maturity=30, n_payment_per_year=12,
):
    """
    Compute the principal payment of a mortgage

    :param: loan_rate, float, the yearly rate of the mortgage
    :param: loan_amount, float, the initial amount borrowed
    :param: years_to_maturity, float, the number of years to repay the mortgage
    :param: n_payment_per_year, int, the number of payments made in a year assumed at a regular
            interval. Typically this should be left to 12.

    >>> compute_mortg_principal(loan_amount=100000, loan_rate=0.025, years_to_maturity=15)
    666.7892090089922
    """

    if loan_rate == 0:
        return loan_amount / (years_to_maturity * n_payment_per_year)
    else:
        period_rate_factor = 1 + loan_rate / n_payment_per_year
        n_periods = years_to_maturity * n_payment_per_year

        # if we don't pay anything off, the loan amount increases after each month, following this function
        total_loan = loan_amount * period_rate_factor ** n_periods

        # if we place a 1 unit at the END of every month at the same rate as the loan rate, this is what we get:
        invest_value_factor = values_of_series_of_invest(
            [loan_rate / n_payment_per_year] * n_periods, [1] * n_periods
        )

        # when the loan is paid off, Principal * invest_value_factor = total_loan so this is the monthly payment:
        return total_loan / invest_value_factor


def compute_equity_and_interest(
    loan_rate=0.025,
    loan_amount=240000,
    years_to_maturity=15,
    n_payment_per_year=12,
    initial_equity=0,
    estate_growth_rate=0,
):
    """
    Return two series, the first one giving the equity over time and the second the interests paid
    to the lender over time.

    :param: loan_rate, float, the yearly rate of the mortgage
    :param: loan_amount, float, the initial amount borrowed
    :param: years_to_maturity, float, the number of years to repay the mortgage
    :param: n_payment_per_year, int, the number of payments made in a year assumed at a regular
            interval. Typically this should be left to 12.
    :param: initial_equity, float, the amount of initial equity, e.g. downpayment or value of the
            purchase above the paid price
    :param: estate_growth_rate, float, expected yearly increase in real estate value
    """

    principal = compute_mortg_principal(
        loan_rate, loan_amount, years_to_maturity, n_payment_per_year
    )
    # initial variable values
    equity = initial_equity
    interest_paid = 0
    remaining_loan = loan_amount
    equity_over_time = [equity]
    interest_paid_over_time = [interest_paid]

    period_interest_factor = loan_rate / n_payment_per_year
    period_estate_growth_factor = 1 + estate_growth_rate / n_payment_per_year

    for period in range(years_to_maturity * n_payment_per_year):
        period_interest = remaining_loan * period_interest_factor
        remaining_loan += period_interest - principal
        interest_paid += period_interest
        equity += principal - period_interest
        equity_over_time.append(equity)
        interest_paid_over_time.append(interest_paid)

    if estate_growth_rate > 0:
        equity_over_time = [
            equ * period_estate_growth_factor ** (n_period + 1)
            for n_period, equ in enumerate(equity_over_time)
        ]

    return equity_over_time, interest_paid_over_time


def inflation_adjust(month_costs_gen, yearly_infl_rate=0.02):
    """
    Given a list of monthly costs, adjust then for inflation so as to have the actual future
    dollar cost
    """
    for i, cost in enumerate(month_costs_gen):
        yield cost * (1 + yearly_infl_rate / 12) ** i


# TODO: each variable is beneficial or not, take that into account to allow ranges


def house_investment(
    mortg_rate=0.0275,
    down_payment_perc=0.2,
    house_cost=240000,
    tax=3000,
    insurance=3000,
    repair=6000,
    estate_rate=0.04,
    mortgage_n_years=15,
    n_years_after_pay_off=10,
    monthly_rental_income=6000,
    percentage_rented=1,
    inflation_rate=0.02,
    income_tax=0.35,
    management_fees_rate=0.22,
    plot=True,
):
    """
    Compute two series, one returning the amount of equity and the second the monthly income
    (positive or negative) from renting the house. The income can then be used in the function
    values_of_series_of_invest to emulate its investment in the stock market for example
    """

    n_months_repay = mortgage_n_years * 12
    n_total_months = n_months_repay + n_years_after_pay_off * 12
    loan_amount = house_cost * (1 - down_payment_perc)
    # get the mortgage monthly cost
    monthly_mort_payment = compute_mortg_principal(
        loan_rate=mortg_rate,
        loan_amount=loan_amount,
        years_to_maturity=mortgage_n_years,
        n_payment_per_year=12,
    )

    # costs are affected by inflation
    # TO DO: Taxes are more affected by the real estate values
    extra_cost_per_month = [(tax + insurance + repair) / 12] * n_total_months
    infl_adj_extra_cost_per_month = inflation_adjust(
        extra_cost_per_month, inflation_rate
    )
    # if rented, a percentage of the cost can be deducted from income
    infl_adj_extra_cost_per_month = [
        cost * (1 - percentage_rented * income_tax)
        for cost in infl_adj_extra_cost_per_month
    ]
    # series of total monthly cost
    total_cost_per_month = [
        cost + monthly_mort_payment * (i <= n_months_repay)
        for i, cost in enumerate(infl_adj_extra_cost_per_month)
    ]

    # series of rental income
    rental_income = [
        monthly_rental_income
        * (1 - management_fees_rate)
        * percentage_rented
        * (1 - income_tax)
        * (1 + estate_rate / 12) ** (i + 1)
        for i in range(n_total_months)
    ]
    # series of monthly balance
    monthly_income = [i[0] - i[1] for i in zip(rental_income, total_cost_per_month)]

    # house values over time
    house_value = [
        house_cost * (1 + estate_rate / 12) ** (i + 1) for i in range(n_total_months)
    ]

    # if nothing were repaid, the loan would follow this
    unrepaid_loan_remaining = [
        loan_amount * (1 + mortg_rate / 12) ** (i + 1) for i in range(n_months_repay)
    ]
    # but we do repay, we can imagine we pay in a different account on the side
    repaid_total = values_of_series_of_invest(
        [mortg_rate / 12] * n_months_repay,
        [monthly_mort_payment] * n_months_repay,
        final_only=False,
    )
    # and the loan balance is the difference between the "unrepaid loan" and what we amass in the
    # side account
    loan_remaining = [i[0] - i[1] for i in zip(unrepaid_loan_remaining, repaid_total)]
    # adding the extra months, where the loan is fully repaid
    loan_remaining += [0] * (n_total_months - n_months_repay)
    # the equity is the difference between the house value and the remaining loan
    equity = [i[0] - i[1] for i in zip(house_value, loan_remaining)]

    if plot:
        plt.plot(equity, label='equity')
        plt.vlines(
            x=n_months_repay,
            ymin=np.min(equity),
            ymax=np.max(equity),
            label='mortgage paid off',
            linestyles='dashed',
            linewidth=0.5,
        )
        plt.xlabel('months')
        plt.ylabel('total')
        plt.legend()
        plt.title(f'Equity over {mortgage_n_years + n_years_after_pay_off} years')
        plt.show()
        plt.plot(monthly_income, label='monthly income')
        plt.vlines(
            x=n_months_repay,
            ymin=np.min(monthly_income + [monthly_mort_payment]),
            ymax=np.max(monthly_income + [monthly_mort_payment]),
            label='mortgage paid off',
            linestyles='dashed',
            linewidth=0.5,
        )
        plt.hlines(
            y=monthly_mort_payment,
            xmin=0,
            xmax=n_total_months,
            label='monthly mortgage payment',
            linestyles='dashed',
            linewidth=0.5,
            color='r',
        )
        plt.xlabel('months')
        plt.ylabel('monthly income')
        plt.legend()
        plt.title(
            f'Monthly income over {mortgage_n_years + n_years_after_pay_off} years'
        )
        plt.show()

    return equity, monthly_income


def compare_house_invest_vs_stock(
    equity,
    monthly_income,
    stock_market_rate=0.08,
    down_payment_perc=0.1,
    house_cost=240000,
    plot=True,
):
    """
    A util function to quickly get a comparison of investments, one in stock and the other in real estate
    """

    stock_market_month_rate = stock_market_rate / 12

    # total house investment. Note that negative income are counted negatively, which
    # is ok since one could assume that the money spent would have been invested in stock otherwise

    positive_monthly_income = [inc * int(inc > 0) for inc in monthly_income]
    negative_monthly_income = [-inc * int(inc <= 0) for inc in monthly_income]

    house_invest = [
        i[0] + i[1]
        for i in zip(
            equity,
            values_of_series_of_invest(
                [stock_market_month_rate] * len(monthly_income),
                positive_monthly_income,
                final_only=False,
                invest_at_begining_of_period=False,
            ),
        )
    ]
    # the same initial investment in stock would yield
    down_payment_invest = [
        down_payment_perc * house_cost * (1 + stock_market_month_rate) ** (i + 1)
        for i in range(len(monthly_income))
    ]
    invested_negative_monthly_income = values_of_series_of_invest(
        [stock_market_month_rate] * len(negative_monthly_income),
        negative_monthly_income,
        final_only=False,
        invest_at_begining_of_period=False,
    )
    total_stock_market_invest = [
        i + j for (i, j) in zip(down_payment_invest, invested_negative_monthly_income)
    ]

    if plot:
        plt.plot(house_invest, label='house')
        plt.plot(down_payment_invest, label='stock')
        plt.legend()
        plt.show()

    return house_invest, total_stock_market_invest
