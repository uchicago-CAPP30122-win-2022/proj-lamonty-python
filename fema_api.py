"""
(la)Monty Python
Ali Klemencic
March 2022

API to connect to OpenFEMA.

Downloads data from the Disaster Declaration Summaries, Web
	Disaster Summaries, and Mission Assignments datasets.

Code adapted from OpenFEMA developer resources: https://www.fema.gov/about/openfema/developer-resources

****************************************************************************************************************
To Do:
	Test code to make sure filter paths correct (is it " " or "_"?)
	Test Pandas dataframe merge code
	Create virtual environment and run in there
	Create requirements.txt
		pip3 freeze > requirements.txt
*****************************************************************************************************************
"""

import requests
import json
import math
import pandas as pd
from api import API


class FemaAPI(API):
	"""
	Class to create an API connection to OpenFEMA for given states and years.
	"""
	base_path = "https://www.fema.gov/api/open"
	record_count_path = "?$inlinecount=allpages&$select=id&$top=1"
	top = 1000

	dataset_dict = {"dds": ("/v2/DisasterDeclarationsSummaries", """?$select=disasterNumber,
							state,declarationDate,fyDeclared,incidentType,declarationTitle,
							incidentBeginDate,incidentEndDate,fipsStateCode,fipsCountyCode"""),
	                "wds": ("/v1/FemaWebDisasterSummaries", """?$select=disasterNumber,
	                        totalAmountIhpApproved,totalAmountHaApproved,totalAmountOnaApproved,
	                        totalObligatedAmountPa,totalObligatedAmountCategoryAb,
	                        totalObligatedAmountCatC2g,totalObligatedAmountHmgp"""),
	                "ms": ("/v1/MissionAssignments", """?$select=disasterNumber,
	                        stateCostShareAmt,federalCostShareAmt,requestedAmount,
	                        obligationAmount,projectedCompletionDate""")}

	def __init__(self, states, years):
		"""
		Constructor.

		:param states: list of states to filter on
		:param years: list of years to filter on
		"""
		self.states = states
		self.years = years
		self.disasters = None
		self.data = pd.DataFrame()


	def get_dds_filter_path(self):
		"""
		Gets the correct filter path for a DDS dataset API call.

		:return: (str) filter path
		"""
		filter_path = "$filter="

		for i, state in enumerate(self.states):
			filter_path += f'(fipsStateCode_eq_{state}'
			if i == len(states) - 1:
				filter_path += ")"
			else:
				filter_path += "_or_"

		for i, year in enumerate(self.years):
			if filter_path[-1] == ")":
				filter_path += "_and_"
			filter_path += f'(fyDeclared_eq_{year}'
			if i != len(states) - 1:
				filter_path += "_or_"
			else:
				filter_path += ")"

		return filter_path


	def get_wds_ms_filter_path(self):
		"""
		Gets the correct filter path for a WDS or MS dataset API call.

		:return: (str) filter path
		"""
		filter_path = "$filter="

		for i, num in enumerate(self.disasters):
			filter_path += f'(disasterNumber_eq_{num}'
			if i == len(disasters) - 1:
				filter_path += ")"
			else:
				filter_path += "_or_"

		return filter_path


	def get_loop_num(cls, dataset, filter_path):
		"""
		Class method to get the number of loops required to
		access every row in the dataset via a quick API call.

		:param dataset: (str) name of the dataset to access
		:param filter_path: (str) filters for the API call

		:return: (int) number of loops required
				and (int) total record count
		"""
		r = requests.get(
			cls.base_path
			+ cls.dataset_dict[dataset][0]
			+ filter_path
			+ cls.record_count_path)
		if r.status_code == 404 or r.status_code == 403:
			raise ValueError("API call failed")
		result = r.text.encode("iso-8859-1")
		json_data = json.loads(result.decode())

		count = json_data['metadata']['count']
		loop_num = math.ceil(count / TOP)

		return loop_num, count


	def get_dataframe(self, dataset, filter_path, loop_num):
		"""
		Calls the API, looping to get all records, and
		generates a dataframe from the resulting json data.

		:param dataset: (str) dataset to connect to
		:param filter_path: (str) filter path
		:param loop_num: (int) number of iterations required

		:return: Pandas dataframe with resulting API call data
		"""
		endpoint, select_path = self.dataset_dict[dataset]
		dataframe = pd.DataFrame()

		skip = 0
		i = 0
		while i < loop_num:
			r = requests.get(
				self.base_path
				+ endpoint
				+ select_path
				+ filter_path
				+ "&$metadata=off&$format=jsona&$skip="
				+ str(skip)
				+ "&$top="
				+ str(self.top)
			)
			result = r.text.encode("iso-8859-1")
			json_data = json.loads(result.decode())

			df = pd.DataFrame(json_data)
			pd.concat([final_dataframe,df])

			i += 1
			skip = i * self.top
			print("Iteration " + str(i) + " done.")

		return dataframe


	def get(self):
		"""
		Gets the data from API calls for each dataset.

		:return: (dict) Pandas dataframes for each dataset
		"""
		dataframes = {}
		keys = ["dds", "wds", "ms"]

		for dataset in keys:
			if dataset == "dds":
				filter_path = self.get_dds_filter_path()
			else:
				self.disasters = dataframes["dds"].disasterNumber.unique()
				filter_path = self.get_wds_ms_filter_path()

			loop_num, count = self.get_loop_num(dataset, filter_path)

			print("Starting " + dataset + " call: " + str(count) + " records, " + str(self.top) +
			      " returned per call, " + str(loop_num) + " iterations needed.")

			df = self.get_dataframe(dataset, filter_path, loop_num)
			dataframes["dataset"] = df

		return dataframes


	def clean_data(self, dataframes):
		"""
		Merges data returned by the API calls.

		:param dataframes: (dict) Pandas dataframes
		                    for each dataset
		"""
		for df in dataframes:
			self.data.join(df.set_index('disasterNumber'), on='disasterNumber')


def make_fema_api_call(states, years):
	api_call = FemaAPI(states, years)
	dataframes = api_call.get()
	api_call.clean_data(dataframes)
	return api_call.data
