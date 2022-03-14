"""
API to connect to OpenFEMA.

(la)Monty Python
Ali Klemencic
March 2022

Code adapted from OpenFEMA developer resources: https://www.fema.gov/about/openfema/developer-resources
"""

import requests
import json
import math
import pandas as pd
from api import API


class FemaAPI(API):
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
		'''
		Constructor.

		Parameters:
			-states: list of states to filter on
			-years: list of years to filter on
		'''
		self.states = states
		self.years = years
		self.disasters = None
		self.dds_df = None
		self.wds_df = None
		self.ms_df = None

	def get_dds_filter_path(self):
		filter_path = "$filter="
		for i, state in enumerate(self.states):
			filter_path += f'(state_eq_{state}'
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
		filter_path = "$filter="
		for i, num in enumerate(self.disasters):
			filter_path += f'(disasterNumber_eq_{num}'
			if i == len(disasters) - 1:
				filter_path += ")"
			else:
				filter_path += "_or_"
		return filter_path

	def get_loop_num(cls, dataset, filter_path):
		# get record count with quick API call
		r = requests.get(
			cls.base_path
			+ cls.dataset_dict[dataset][0]
			+ filter_path
			+ cls.record_count_path)
		result = r.text.encode("iso-8859-1")
		json_data = json.loads(result.decode())
		count = json_data['metadata']['count']
		loop_num = math.ceil(count / TOP)
		return loop_num, count

	def get_json_file(self, parameters):
		dataset, endpoint, select_path, filter_path, loop_num = parameters
		# initialize json file
		filename = dataset + "_output.json"
		output_file = open(filename, "a")
		# FEMA website said to pull in as a list under key named that dataset. is this best practice?
		output_file.write('[')
		# loop and call API changing record start for each iteration
		i = 0
		skip = 0
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

			# append results to file, trimming off first/last JSONA brackets, adding comma
			# except for last call, and terminating array bracket and brace on the last call
			if i == loop_num - 1:
				output_file.write(str(result[1:-1], 'utf-8') + "]}")
			else:
				output_file.write(str(result[1:-1], 'utf-8') + ",")

			i += 1
			skip = i * self.top

			# announce know what's happening
			print("Iteration " + str(i) + " done.")

		output_file.close()
		return filename

	def get_json_for_each_dataset(self):
		filenames = {}
		for dataset, (endpoint, select_path) in self.dataset_dict.items():
			# get filters for dataset
			if dataset == "dds":
				filter_path = self.get_dds_filter_path()
			else:
				self.disasters = self.dds_df.disasterNumber.unique()
				filter_path = self.get_wds_ms_filter_path()

			loop_num, count = self.get_loop_num(dataset, filter_path)

			# announce know what's happening
			print("Starting " + dataset + " call: " + str(count) + " records, " + str(self.top) +
			      " returned per call, " + str(loop_num) + " iterations needed.")

			parameters = (dataset, endpoint, select_path, filter_path, loop_num)
			filename = self.get_json_file(parameters)
			df = pd.read_json(filename)
			if dataset == "dds":
				self.dds_df = df
			elif datset == "wds":
				self.wds_df = df
			elif dataset == "ms":
				self.ms_df = df

	def gen_pandas_dataframe(self):
		self.get_json_for_each_dataset()

		interim_df = self.dds_df.join(self.wds_df.set_index('disasterNumber'), on='disasterNumber')
		final_df = interim_df.join(self.ms_df.set_index('disasterNumber'), on='disasterNumber')

		return final_df


def make_fema_api_call(states, years):
	api_call = FemaAPI(states, years)
	dataframe = api_call.gen_pandas_dataframe()
	return dataframe
