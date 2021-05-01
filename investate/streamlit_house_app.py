import streamlit as st
import numpy as np
import pandas as pd

st.title('Quadratic app')

st.latex(r''' ax^2+bx+c ''')
a = st.number_input('Enter first coeff')
b = st.number_input('Enter 2nd')
c = st.number_input('Enter 3rd')


def mk_quadratic_func(a, b, c):
    func = lambda x: a * x ** 2 + b * x + c
    return func


domain = np.linspace(-10, 10, 1000)
vals = mk_quadratic_func(a, b, c)(domain)
df = pd.DataFrame()
df['vals'] = vals
st.line_chart(df)
