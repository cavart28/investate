import pytest
from investate.real_estate_vs_stock import *


@pytest.mark.parametrize("invest_amounts,rate_between_amounts,final_only,invest_at_begining_of_period", [
    ([0], [0.2], True, False),
    ([0, 0], [0.2, 0.05], True, False),
])
def test_values_of_series_of_invest(invest_amounts, rate_between_amounts, final_only, invest_at_begining_of_period):
    res = values_of_series_of_invest(invest_amounts, rate_between_amounts, final_only, invest_at_begining_of_period)
    assert res == 0


@pytest.mark.parametrize("loan_rate,loan_amount,years_to_maturity,n_payment_per_year", [
    (0.1, 200, 10, 12),
    (0.2, 100, 20, 12),
    (1, 10, 2, 10),
    (0.1, -100, 10, 1),
    (0.001, 10, 100, 3),
    (0.265, 216000, 15, 12)
])
def test_compute_mortg_principal(loan_rate, loan_amount, years_to_maturity, n_payment_per_year):
    principal = compute_mortg_principal(loan_rate, loan_amount, years_to_maturity, n_payment_per_year)
    n_periods = n_payment_per_year * years_to_maturity
    reg_payment = values_of_series_of_invest([principal] * n_periods,
                                             [loan_rate / n_payment_per_year] * n_periods)
    loan_left_unpaid = loan_amount * (1 + loan_rate / n_payment_per_year) ** (n_payment_per_year * years_to_maturity)

    assert np.isclose(reg_payment, loan_left_unpaid)
