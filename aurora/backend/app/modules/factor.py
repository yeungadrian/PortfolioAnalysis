from typing import List, TypeVar

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pydantic import BaseModel

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


class FactorAnalysis(BaseModel):
    fund_codes: List[str]
    start_date: str
    end_date: str
    factors: List[str]
    fund_returns: PandasDataFrame
    ff_factors: PandasDataFrame

    def get_summary_results(self, results, fund_code):
        """take the result of an statsmodel results table and transforms it into a dataframe
        https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.html"""
        pvals = results.pvalues
        coefficient = results.params
        conf_lower = results.conf_int()[0]
        conf_higher = results.conf_int()[1]
        standard_errors = results.bse
        residuals = results.resid
        num_obs = results.nobs
        rsquared = results.rsquared
        rsquared_adj = results.rsquared_adj
        fvalue = results.fvalue

        output_result = {
            "fund_code": fund_code,
            "num_obs": num_obs,
            "rsquared": rsquared,
            "rsquared_adj": rsquared_adj,
            "fvalue": fvalue,
            "coefficient": coefficient,
            "standard_errors": standard_errors,
            "pvals": pvals,
            "conf_lower": conf_lower,
            "conf_higher": conf_higher,
            "residuals": residuals,
        }

        return output_result

    def calculate_factor_regression(self, fund_code, regression_factors):

        np.random.seed(1000)

        regression_equation = " + ".join(regression_factors)
        fund_returns = self.fund_returns.copy()
        ff_factors = self.ff_factors.copy()

        print(fund_returns["date"])
        fund_returns["date"] = fund_returns["date"].dt.strftime("%Y-%m-%d")
        ff_factors["date"] = ff_factors["date"].dt.strftime("%Y-%m-%d")

        fund_returns = fund_returns.set_index("date")
        fund_returns.index.name = None

        ff_factors = ff_factors.set_index("date")
        ff_factors.index.name = None

        regression_data = pd.concat([fund_returns, ff_factors], axis=1, join="inner")

        regression_data[fund_code] = regression_data[fund_code] - regression_data["RF"]

        model = smf.ols(
            formula=f"{fund_code} ~ {regression_equation}", data=regression_data
        )

        results = model.fit()

        output = self.get_summary_results(results, fund_code)

        return output

    def regress_funds(self):
        output = []

        for i in self.fund_codes:
            output.append(self.calculate_factor_regression(i, self.factors))
        return output
