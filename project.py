""" Smart wealth projector

The smart wealth projector is a simple wealth projector that takes into
account many more factors than those currently available, including
income increase, spending patterns, taxation, and home purchase.
Calculate when you will become a millionnaire~!
"""
import copy
from projector import Portfolio, CashFlow, Asset, Loan, format_worth


casual_spending_increase_rate = 1.04
portfolio = Portfolio(
    initial_value=40000,
    investment_return_rate=1.1,
    inflation_rate=1.0325,
    incomes=[CashFlow(162778, 1.04)],
    spendings=[CashFlow(60000, casual_spending_increase_rate)],
    tax_deductions=[
        CashFlow(19500, 1.025),  # 401(k)
    ],
)

for year in range(70):
    if year % 10 == 0 and year:
        print()
        print(f'# {year} years from now')
        print()
        print(portfolio)
    if year == 4:  # Buy a home 4 years later
        home_loan = Loan(1000000, 0.0575, 10)
        portfolio.incomes = [
            CashFlow(184229, 1.19, 480661),
            CashFlow(2400, 1.1022),
        ]
        portfolio.spendings = [
            # Less spending because you don't need to pay rent
            CashFlow(40000, casual_spending_increase_rate),
            CashFlow(10000, 1.0816),  # Property tax
            home_loan.get_spending(),  # Home loan payment
        ]
        portfolio.tax_deductions.extend([
            CashFlow(10000, 1.0816),  # Property tax deducts income tax
            home_loan.get_tax_deduction(),  # Home loan interest deducts tax
        ])
        portfolio.assets.extend([
            Asset(1000000, 1.0816),  # Home
            home_loan,  # Home loan as a negative asset
        ])
    portfolio.step()
