TAX_BRACKETS = [
    (0, 9700, 0.1),
    (9700, 39475, 0.12),
    (39475, 84200, 0.22),
    (84200, 160725, 0.24),
    (160726, 204100, 0.32),
    (204100, 306750, 0.35),
    (306750, float('inf'), 0.37),
]

def format_worth(label, value):
    dollar_string = f'{value:,.02f}'.rjust(15)
    string = f'{label:20s}{dollar_string}'
    return string


def get_income_tax(amount):
    tax = 0
    for lower_limit, upper_limit, rate in TAX_BRACKETS:
        tax += min(max(amount - lower_limit, 0), upper_limit) * rate
    return tax


class CashFlow:

    def __init__(
        self, starting_value, growth_rate=1, saturation_value=float('inf'),
        lifespan=float('inf')
    ):
        self.value = starting_value
        self.growth_rate = growth_rate
        self.saturation_value = saturation_value
        self.lifespan = lifespan
    
    def step(self):
        self.lifespan -= 1
        if self.lifespan > 0:
            self.value = min(
                self.value * self.growth_rate, self.saturation_value
            )
        else:
            self.value = 0


class Asset:

    def __init__(self, starting_value, growth_rate=1):
        self.value = starting_value
        self.growth_rate = growth_rate
    
    def asset_growth(self):
        growth = self.value * (self.growth_rate - 1)
        return growth

    def step(self):
        self.value = self.value * self.growth_rate


class Loan(Asset):

    def __init__(self, amount, rate, length):
        self.principal_amount = amount
        self.payment_amount = rate * amount / (1 - (1 + rate) ** -length)
        self.length = length
        self.value = -self.payment_amount * length

    def asset_growth(self):
        growth = self.payment_amount if self.value < 0 else 0
        return growth

    def step(self):
        self.value = min(self.value + self.payment_amount, 0)
    
    def get_spending(self):
        spending = CashFlow(self.payment_amount, lifespan=self.length)
        return spending

    def get_tax_deduction(self):
        deduction = CashFlow(
            self.payment_amount - self.principal_amount / self.length,
            lifespan=self.length
        )
        return deduction


class Portfolio:

    def __init__(
        self,
        initial_value=0,
        investment_return_rate=1,
        inflation_rate=1,
        incomes=[],
        spendings=[],
        tax_deductions=[],
        assets=[],
    ):
        self.liquid_value = initial_value
        self.investment_return_rate = investment_return_rate
        self.inflation = CashFlow(1, inflation_rate)
        self.incomes = incomes
        self.spendings = spendings
        self.tax_deductions = tax_deductions
        self.assets = assets

    def total_income(self):
        income = self._get_total_value(self.incomes)
        return income

    def tax_deduction(self):
        deduction = self._get_total_value(self.tax_deductions)
        return deduction

    def investment_return(self):
        return_ = self.liquid_value * (self.investment_return_rate - 1)
        return return_
    
    def asset_value(self):
        value = sum(asset.value for asset in self.assets)
        return value
    
    def asset_growth(self):
        growth = sum(asset.asset_growth() for asset in self.assets)
        return growth

    def spending(self):
        spending = self._get_total_value(self.spendings)
        return spending

    @classmethod
    def _get_total_value(cls, cash_flows):
        value = 0 if not cash_flows else sum(
            flow.value for flow in cash_flows
        )
        return value

    def step(self):
        for income in self.incomes:
            income.step()
        for tax_deduction in self.tax_deductions:
            tax_deduction.step()
        for spending in self.spendings:
            spending.step()
        for asset in self.assets:
            asset.step()
        self.inflation.step()
        self.liquid_value = (
            self.liquid_value
            + self.total_income()
            - get_income_tax(self.total_income() - self.tax_deduction())
            + self.investment_return()
            - self.investment_return() * 0.2
            - self.spending()
        )

    def total_value(self):
        value = self.liquid_value + self.asset_value()
        return value
    
    def deflated_value(self):
        value = self.total_value() / self.inflation.value
        return value
