if __name__ == "__main__":

    from investate.investate.real_estate_vs_stock import *

    # equity_over_time, interest_paid_over_time = compute_equity_and_interest(
    #     loan_rate=0.025,
    #     loan_amount=240000,
    #     years_to_maturity=15,
    #     n_payment_per_year=12,
    #     initial_equity=0,
    #     estate_growth_rate=0.05)
    # plt.plot(equity_over_time, label='equity'), plt.plot(interest_paid_over_time, label='interests paid');
    # plt.legend()

    # mortg_rate = 0.0265
    # down_payment_perc = 0.1
    # house_cost = 240000
    # tax = 4000
    # insurance = 3000
    # repair = 6000
    # estate_rate = 0.03
    # mortgage_n_years = 15
    # n_years_after_pay_off = 10
    # monthly_rental_income = 7500
    # inflation_rate = 0.02
    # percentage_rented = 0.3
    # income_tax = 0.35
    # management_fees_rate = 0.22
    #
    # # equity and montly_income are saved in variables to use in the next function which
    # # compares the downpayment + monthly cost investment with the same in the stock market
    # equity, monthly_income = house_investment(mortg_rate=mortg_rate,
    #                                           down_payment_perc=down_payment_perc,
    #                                           house_cost=house_cost,
    #                                           tax=tax,
    #                                           insurance=insurance,
    #                                           repair=repair,
    #                                           estate_rate=estate_rate,
    #                                           mortgage_n_years=mortgage_n_years,
    #                                           n_years_after_pay_off=n_years_after_pay_off,
    #                                           monthly_rental_income=monthly_rental_income,
    #                                           inflation_rate=inflation_rate,
    #                                           percentage_rented=percentage_rented,
    #                                           income_tax=income_tax,
    #                                           management_fees_rate=management_fees_rate,
    #                                           plot=False)
    #
    # house_invest, down_payment_invest = compare_house_invest_vs_stock(equity, monthly_income, plot=True)

    princ = compute_mortg_principal(loan_rate=0.04,
                                    loan_amount=1000,
                                    years_to_maturity=10,
                                    n_payment_per_year=12)
    print(princ)

    print(values_of_series_of_invest([princ] * 120,
                                     [0.04 / 12] * 120,
                                     final_only=True))
    print(1000 * (1+0.04/12)**120)

