"""
Script which contains the main logic of the app, putting all together

The process consists of the following steps:

1 - Drop the bundle if it exists and create it again (for now, in behalf of simplicity, so we will not have to calculate deltas)

2 - Download Power Bi reports from the Power BI Report Server and extract their M scripts

3 - Parse the M scripts and get the metadata ready for loading on IGC(which is XML oriented)

4 - generate the XML from metadata and upload it to IGC

"""

#import my libs
import powerapi
from repository import Repository
import pqparser as pqp #pq stands for Power Query, dont get me wrong
import numpy as np
from igcapi import igc

#get environment variables from .env file
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#Create objects to manipulate the PbiServer, local repository and IGC rest api
pbi = powerapi.PbiServer()
repo = Repository()
igc = igc()


igc.internal_id

# Step 1: truncate all objects (temporary)
r = igc.delete_bundle()

# Step 2: Register bundle
result = igc.register_bundle(repo)

# Step 3: Download Power BI db2_reports
#pbi.download_all_reports(repo)

# Step 4: Extract the M scripts of all reports
#repo.extract_pbi_queries()

# Step 5: Generate a pandas dataframe for hosts, folders, reports and schemas


reports = pbi.get_report_list()

reports

import numpy as np

#function applying methods:
reports['db2'] = np.vectorize(pqp.has_db2_sources)(reports['itemid'])
#reports['db2'] = reports['db2'].map(pqp.has_db2_sources)

db2_reports = reports[reports.db2].reset_index()

db2_reports['itemid'][0]

meta = pqp.get_metadata(db2_reports['itemid'][0])

meta

query = meta[0].get('query')

query_meta = pqp.get_query_from_tables.findall(query)

query_meta
