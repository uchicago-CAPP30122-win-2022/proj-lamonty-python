"""
Abstract API class.

(la)Monty Python
Ali Klemencic
March 2022
"""

from abc import ABC, abstractmethod


class API(ABC):

	@abstractmethod
	def get(self):
		pass

	@abstractmethod
	def clean_data(self, dataframes):
		pass



"""
FEMA API
	Get Method
		get loops
		call api
		return pandas dfs for each dataset
	Clean Data Method
		merge data
		clean anything wrong
		

Census API
	Get Method
		get detail county data
		get data profile data
	Clean Data Method
		merge data
		cleans data
"""
