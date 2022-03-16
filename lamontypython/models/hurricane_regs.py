"""
Regression class that performs specified 
regressions.

(la)Monty Python
Wesley Janson
March 2022
"""
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
from patsy import dmatrices
import numpy as np
import pandas as pd
from backend import datasets

class Disaster_regs():
    '''
    Class for running natural disaster regressions.
    '''

    hurricane_dict = {"Harvey": (["22","48"],[2017]),
                        "Irma": (["01","12","13","28","45","47"],[2017]),
                        "Sandy": (["09","10","11","24","34","36","42","51","54"],[2012]),
                        "Maria": (["72"],[2017])}

    variable_dict = {'foreign_born':'Percentage of county population born outside U.S.',
                'black_afam':'Percentage of county population Black/African American.',
                'median_income':'Median household income (in nominal dollars).',
                'snap_benefits':'Percentage of county households on SNAP benefits in the last 12 months.',
                'unemp_rate':'County unemployment rate for prime-age workers.',
                'health_insurance_rate':'Percentage of county population with health insurance coverage.',
                'vacant_housing_rate':'Percentage of housing units vacant at time of survey.',
                'rental_vacancy_rate':'Percentage of rental units vacant at time of survey.',
                'median_rent':'Median gross rent at county level (in nominal dollars).',
                'median_home_price':'Median home price at county level (in nominal dollars).'}


    def __init__(self, hurricane,reg_type):
        '''
		Constructor.

        Parameters:
			-hurricane: list of states to filter on corresponding
            to specific hurricane.
		'''
        self.hurricane = hurricane
        self.reg_type = reg_type


    def pull_data(self):
        '''
        Method that will pull data using API abstract class.
        '''
        self.states,self.year = self.hurricane_dict[self.hurricane]
        self.dataframe = datasets.get_data(self.states,self.year)

        return self.dataframe
    

    def pooled_ols(self,dataset):
        '''
        Method to run simple pooled OLS regression.
        '''
        y = pd.DataFrame(dataset, columns=['aid_requested'])
        exog_vars = self.vif_detection(pd.DataFrame(dataset, columns=['foreign_born','black_afam','median_income','snap_benefits','unemp_rate',
        'health_insurance_rate','vacant_housing_rate','rental_vacancy_rate','median_rent','median_home_price','population']),y)
        var_table = self.var_table(exog_vars)
        X = sm.add_constant(exog_vars)
        pooled_reg = sm.OLS(y,X).fit()

        return self.output_to_df(pooled_reg,"pooled"),y.merge(exog_vars, left_index=True, right_index=True),var_table


    def panel_ols(self,dataset):
        '''
        Method running Fixed Effect regression. The state is set to be the panel variable, 
        with the year being the time variable.
        '''
        y = pd.DataFrame(dataset, columns=['aid_requested'])
        exog_vars = self.vif_detection(pd.DataFrame(dataset, columns=['foreign_born','black_afam','median_income','snap_benefits','unemp_rate',
        'health_insurance_rate','vacant_housing_rate','rental_vacancy_rate','median_rent','median_home_price','population']),y)
        var_table = self.var_table(exog_vars)

        dataset['year'] = pd.to_datetime(dataset.year, format='%Y')
        dataset.astype({'state_fips': 'int32'}).dtypes
        dataset = dataset.set_index(['state_fips','year'])
        
        fe_reg = PanelOLS(y, sm.add_constant(exog_vars), entity_effects=True, time_effects=False).fit(cov_type='robust') 

        return self.output_to_df(fe_reg,"fe"),y.merge(exog_vars, left_index=True, right_index=True),var_table


    def output_to_df(self,reg_output,reg_type):
        '''
        Method taking regression summary table and saves in clean pandas df.
            For readability, the numbers in the table are rounded to thousandths
            decimal place.

        Input:
            -reg_output: regression output table to be converted.
        '''
        coefs = reg_output.params
        pvals = reg_output.pvalues
        if reg_type=="pooled":
            std_err = reg_output.bse
            tvals = reg_output.tvalues            
        else:
            std_err = reg_output.std_errors
            tvals = reg_output.tstats
        
        out_df = pd.DataFrame({"Coefficient Estimate":coefs, "Standard Error":std_err,
                            "T-Stat":tvals, "P-Value":pvals})

        return out_df.round(decimals=3)


    def vif_detection(self,exog_vars,dep_var):
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
            _, X = dmatrices(reg_string, data=self.dataframe, return_type='dataframe')
            vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
            max_vif = max(vif[1:])
            if max_vif > 5:
                max_col = vif.index(max_vif)
                exog_vars = exog_vars.drop(exog_vars.columns[max_col-1], axis=1)

        return exog_vars


    def var_table(self,exog_vars):
        '''
        Method to take exogenous variables used in regression and create corresponding
        variable description table to be displayed on UI page.
        '''
        desc_list=[]
        for var in exog_vars.columns:
            desc_list.append(self.variable_dict[var])

        return pd.DataFrame({"Independent Variable":exog_vars.columns, "Description":desc_list})



def run_regressions(hurricane,reg_type):
    '''
    Performs Disaster_regs class, using input given from user
        selection to run specified regression from specified hurricane.
    '''
    reg = Disaster_regs(hurricane,reg_type)
    dataset = reg.pull_data()
    if reg_type == "pooled":
        reg_output,reg_data,var_table = reg.pooled_ols(dataset)
    elif reg_type == "fe":
        reg_output,reg_data,var_table = reg.panel_ols(dataset)
    
    return reg_output,reg_data,var_table
