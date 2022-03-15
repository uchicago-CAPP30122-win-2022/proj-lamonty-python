"""
(la)Monty Python
Ali Klemencic
March 2022

API to connect to OpenFEMA. Downloads data from the Disaster
Declaration Summaries and Web Disaster Summaries datasets.

Code adapted from OpenFEMA developer resources:
https://www.fema.gov/about/openfema/developer-resources.
"""

import json
import math
import requests
import pandas as pd
from data.apis.api import API


class FEMAapi(API):
    """
    Class to connect to OPENFema via API.
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
                            totalObligatedAmountCatC2g,totalObligatedAmountHmgp""")}

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
        filter_path = "&$filter=("

        for i, state in enumerate(self.states):
            filter_path += f"fipsStateCode eq '{state}'"
            if i == len(self.states) - 1:
                filter_path += ")"
            else:
                filter_path += " or "

        for i, year in enumerate(self.years):
            if filter_path[-1] == ")":
                filter_path += " and ("
            filter_path += f"fyDeclared eq '{year}'"
            if i == len(self.years) - 1:
                filter_path += ")"
            else:
                filter_path += " or "

        return filter_path


    def get_wds_filter_path(self):
        """
        Gets the correct filter path for a WDS dataset API call.

        :return: (str) filter path
        """
        filter_path = "&$filter=("

        for i, num in enumerate(self.disasters):
            filter_path += f'disasterNumber eq {num}'
            if i == len(self.disasters) - 1:
                filter_path += ")"
            else:
                filter_path += " or "

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
            + cls.record_count_path
            + filter_path)
        if r.status_code != 200:
            raise ValueError("API call failed")
        result = r.text.encode("iso-8859-1")
        json_data = json.loads(result.decode())

        count = json_data['metadata']['count']
        loop_num = math.ceil(count / cls.top)

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
                + select_path.replace("\n", "")
                + filter_path
                + "&$metadata=off&$format=jsona&$skip="
                + str(skip)
                + "&$top="
                + str(self.top)
            )
            if r.status_code != 200:
                raise ValueError("API call failed")
            result = r.text.encode("iso-8859-1")
            json_data = json.loads(result.decode())

            df = pd.DataFrame(json_data)
            dataframe = pd.concat([dataframe,df])

            i += 1
            skip = i * self.top
            print("Iteration " + str(i) + " done.")

        return dataframe


    def get_data(self):
        """
        Gets the data from API calls for each dataset.

        :return: (dict) Pandas dataframes for each dataset
        """
        dataframes = {}
        keys = ["dds", "wds"]

        for dataset in keys:
            if dataset == "dds":
                filter_path = self.get_dds_filter_path()
            else:
                self.disasters = dataframes["dds"].disasterNumber.unique()
                filter_path = self.get_wds_filter_path()

            loop_num, count = self.get_loop_num(dataset, filter_path)

            print("Starting " + dataset + " call: " + str(count) + " records, " + str(self.top) +
                  " returned per call, " + str(loop_num) + " iterations needed.")

            dataframes[dataset] = self.get_dataframe(dataset, filter_path, loop_num)

        return dataframes


    def clean_data(self, dataframes):
        """
        Merges data returned by the API calls.

        :param dataframes: (dict) Pandas dataframes for each dataset
        """
        for _, df in dataframes.items():
            df = df.drop(['id'], axis=1)
            df = df.set_index('disasterNumber')
            if self.data.empty:
                self.data = df
            else:
                self.data = self.data.join(df, on='disasterNumber')

        self.data = self.data.rename(columns={'declarationDate': 'declaration_date',
                                    'fyDeclared': 'year',
                                    'incidentType': 'incident_type',
                                    'declarationTitle': 'disaster_name',
                                    'incidentBeginDate': 'incident_begin_date',
                                    'incidentEndDate': 'incident_end_date',
                                    'fipsStateCode': 'state_fips',
                                    'fipsCountyCode': 'county_fips',
                                    'totalAmountIhpApproved': 'total_approved_ihp',
                                    'totalAmountHaApproved': 'total_approved_ha',
                                    'totalAmountOnaApproved': 'total_approved_ona',
                                    'totalObligatedAmountPa': 'total_obligated_pa',
                                    'totalObligatedAmountCategoryAb': 'total_obligated_ab',
                                    'totalObligatedAmountCatC2g': 'total_obligated_c2g',
                                    'totalObligatedAmountHmgp': 'total_obligated_hmgp'})

        self.data['total_approved'] = self.data.get('total_approved_ihp', 0) \
                                      + self.data.get('total_approved_ha', 0) \
                                      + self.data.get('total_approved_ona', 0)

        self.data['total_obligated'] = self.data.get('total_obligated_pa', 0) \
                                        + self.data.get('total_obligated_ab', 0) \
                                        + self.data.get('total_obligated_c2g', 0) \
                                        + self.data.get('total_obligated_hmgp', 0)
