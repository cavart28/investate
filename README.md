# Investate

A collection of tools to find the value over time of various investments, mainly to compare with real estate investment

You ask the question:
"How much would I have if I invest every month $10 on a bank account at a rate of 5%"
You could use basic calculus to find the answer. Now imagine a more realistic situation where you invest various amount
or that the monthly rate varies from month to month. For example you invest successively $10, $12 and $5 and monthly
rates of 1%, 0.5% and 1.1%.
Then the answer is:

values_of_series_of_invest([10, 12, 5], [0.01, 0.005, 0.011])