"""
Abstract API class.

(la)Monty Python
Ali Klemencic
March 2022
"""

from abc import ABC, abstractmethod

class API(ABC):

	@abstractmethod
	def get_json_file(self, parameters):
		pass

	@abstractmethod
	def gen_pandas_dataframe(self):
		pass