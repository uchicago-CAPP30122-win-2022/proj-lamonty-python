#### Testing Regressions
#pip install linearmodels
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
from patsy import dmatrices
import numpy as np
import pandas as pd

data = pd.read_csv("analysis_state_years.csv", header=0)

hurricane_dict = {"Harvey": (["22","48"],2017),
                        "Irma": (["01","12","13","28","45","47"],2017),
                        "Sandy": (["09","10","11","24","34","36","42","51","54"],2012),
                        "Maria": (["72"],2017)}

variable_dict = {'population':'County-level population.',
                'foreign_born':'Percentage of county population born outside U.S.',
                'black_afam':'Percentage of county population Black/African American.',
                'median_income':'Median household income (in nominal dollars).',
                'snap_benefits':'Percentage of county households on SNAP benefits in the last 12 months.',
                'unemp_rate':'County unemployment rate for prime-age workers.',
                'health_insurance_rate':'Percentage of county population with health insurance coverage.',
                'vacant_housing_rate':'Percentage of housing units vacant at time of survey.',
                'rental_vacancy_rate':'Percentage of rental units vacant at time of survey.',
                'median_rent':'Median gross rent at county level (in nominal dollars).',
                'median_home_price':'Median home price at county level (in nominal dollars).'}

states,year = hurricane_dict["Irma"]

states=[9,10,11,24,34,36,42,51,54]
data = data.loc[data['state_fips'].isin(states)]
data = data.loc[data['year'] == year]

def vif_detection(exog_vars,dep_var):
        '''
        Method computing Variance Inflation Factors (VIF) on prospective exogenous variables for regression. 
        5 (inclusive) is used as the cutoff for multicollinearity. This function eliminiates the variable with 
        the highest VIF, and reruns the regression until the highest VIF is below the threshold.

        Input:
            -exog_vars (pandas df): pandas dataframe of potential exogenous variables for regression.
            -dep_var (pandas series): pandas dataframe of dependent variable in regression.
        '''
        max_vif = float('inf')
        while max_vif > 5:
            reg_string = dep_var.columns[0] + ' ~ ' + '+'.join(exog_vars.columns)
            _, X = dmatrices(reg_string, data=data, return_type='dataframe')
            vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
            max_vif = max(vif[1:])
            if max_vif > 5:
                max_col = vif.index(max_vif)
                exog_vars = exog_vars.drop(exog_vars.columns[max_col-1], axis=1)

        return exog_vars

# Panel Reg-Output at the end
y = pd.DataFrame(data, columns=['aid_requested'])
exog = pd.DataFrame(data, columns=['foreign_born','black_afam','median_income','snap_benefits','unemp_rate','health_insurance_rate','vacant_housing_rate','rental_vacancy_rate','median_rent','median_home_price','population'])
exog_vars = vif_detection(exog,y)
X = sm.add_constant(exog_vars)
pooled_reg = sm.OLS(y,X).fit()

coefs = pooled_reg.params
std_err = pooled_reg.bse
tvals = pooled_reg.tvalues
pvals = pooled_reg.pvalues

results_df = pd.DataFrame({"Coefficient Estimate":coefs, "Standard Error":std_err, "T-Stat":tvals, "P-Value":pvals})

results_df.round(decimals=3)


#Create variable table
desc_list=[]
for var in exog_vars.columns:
    desc_list.append(variable_dict[var])

var_df = pd.DataFrame({"Independent Variable":exog_vars.columns, "Description":desc_list})
var_df


# Data from regression
reg_data = y.merge(exog_vars, left_index=True, right_index=True)
reg_data