import pytest
from investate.investate.real_estate_vs_stock import *


@pytest.mark.parametrize("invest_amounts,rate_between_amounts,final_only,invest_at_begining_of_period", [
    ([0], [0.2], True, False),
    ([0, 0], [0.2, 0.05], True, False),
])
def test_values_of_series_of_invest(invest_amounts, rate_between_amounts, final_only, invest_at_begining_of_period):
    res = values_of_series_of_invest(invest_amounts, rate_between_amounts, final_only, invest_at_begining_of_period)
    assert res == 0

