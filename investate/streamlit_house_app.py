"""
Little streamlit app to help make decision on whether to invest in real estate vs stock market
"""

import streamlit as st
import pandas as pd
from investate.real_estate_vs_stock import (
    house_investment,
    compare_house_invest_vs_stock,
)

st.title('House vs other investment')

house_cost = st.sidebar.number_input('House price', value=240000)
down_payment_perc = (
    st.sidebar.number_input('Down payment percentage', value=10) * 0.01
)
mortg_rate = st.sidebar.number_input('Mortgage rate', value=2.75) * 0.01
mortgage_n_years = st.sidebar.number_input(
    'Mortgage duration in years', value=15
)
n_years_after_pay_off = st.sidebar.number_input(
    'Years to display after pay off', value=5
)

tax = st.sidebar.number_input('Yearly tax', value=4000)
insurance = st.sidebar.number_input('Yearly insurance cost', value=3000)
repair = st.sidebar.number_input('Yearly repair cost', value=6000)
monthly_rental_income = st.sidebar.number_input(
    'Average monthly rental income', value=7500
)
percentage_rented = st.sidebar.number_input('Percentage rented', value=0.5)


estate_rate = (
    st.sidebar.number_input('Yearly real estate market increase', value=3.5)
    * 0.01
)
inflation_rate = st.sidebar.number_input('Inflation rate', value=2.1) * 0.01
income_tax = st.sidebar.number_input('Income tax percentage', value=33) * 0.01
management_fees_rate = (
    st.sidebar.number_input('Management fees', value=22) * 0.01
)
stock_market_rate = (
    st.sidebar.number_input('Yearly rate of other investment', value=8) * 0.01
)


equity, monthly_income = house_investment(
    mortg_rate,
    down_payment_perc,
    house_cost,
    tax,
    insurance,
    repair,
    estate_rate,
    mortgage_n_years,
    n_years_after_pay_off,
    monthly_rental_income,
    percentage_rented,
    inflation_rate,
    income_tax,
    management_fees_rate,
    plot=False,
)

df = pd.DataFrame()
df['equity'] = equity
df['montlhy_income'] = monthly_income


house_invest, down_payment_invest = compare_house_invest_vs_stock(
    equity,
    monthly_income,
    stock_market_rate=stock_market_rate,
    down_payment_perc=down_payment_perc,
    house_cost=house_cost,
    plot=False,
)
df['house_investment'] = house_invest
df['stock_investment'] = down_payment_invest

st.line_chart(df['montlhy_income'])
st.line_chart(df['equity'])
st.line_chart(df[['house_investment', 'stock_investment']])
