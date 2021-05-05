import streamlit as st
import numpy as np
import pandas as pd
from investate.investate.real_estate_vs_stock import house_investment, compare_house_invest_vs_stock

st.title('House vs other investment')

cols = st.beta_columns(3)

house_cost = cols[0].number_input('House price', value=240000)
down_payment_perc = cols[0].number_input('Down payment percentage', value=10) * 0.01
mortg_rate = cols[0].number_input('Mortgage rate', value=2.75) * 0.01
mortgage_n_years = int(cols[0].number_input('Mortgage duration in years', value=15))
n_years_after_pay_off = cols[0].number_input('Years to display after pay off', value=5)

tax = cols[1].number_input('Yearly tax', value=4000)
insurance = cols[1].number_input('Yearly insurance cost', value=3000)
repair = cols[1].number_input('Yearly repair cost', value=6000)
monthly_rental_income = cols[1].number_input('Average monthly rental income', value=7500)
percentage_rented = cols[1].number_input('Percentage rented', value=0.5)


estate_rate = cols[2].number_input('Yearly real estate market increase', value=3.5) * 0.01
inflation_rate = cols[2].number_input('Inflation rate', value=2.1) * 0.01
income_tax = cols[2].number_input('Income tax percentage', value=33) * 0.01
management_fees_rate = cols[2].number_input('Management fees', value=22) * 0.01
stock_market_rate = cols[2].number_input('Yearly rate of other investment', value=8) * 0.01


equity, monthly_income = house_investment(mortg_rate,
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
                                          plot=False)

df = pd.DataFrame()
df['equity'] = equity
df['monthy_income'] = monthly_income


house_invest, down_payment_invest = compare_house_invest_vs_stock(equity,
                                                                  monthly_income,
                                                                  stock_market_rate=stock_market_rate,
                                                                  down_payment_perc=down_payment_perc,
                                                                  house_cost=house_cost,
                                                                  plot=False)
df['house_invest'] = house_invest
df['down_payment_invest'] = down_payment_invest

st.line_chart(df['monthy_income'])
st.line_chart(df[['equity', 'house_invest', 'down_payment_invest']])
