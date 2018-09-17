#import my libs
import powerapi
from repository import Repository
import pqparser as pqp #pq stands for Power Query, dont get me wrong
import numpy as np

#get environment variables from .env file
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#create a Power Bi Server connection and a local repository of files
pbi = powerapi.PbiServer()
repo = Repository()

#pbi.download_all_reports(repo)
#repo.extract_pbi_queries()

reports = pbi.get_report_list()

import numpy as np

#function applying methods:
reports['db2'] = np.vectorize(pqp.has_db2_sources)(reports['itemid'])
#reports['db2'] = reports['db2'].map(pqp.has_db2_sources)

db2_reports = reports[reports.db2].reset_index()

db2_reports['itemid'][0]

meta = pqp.get_metadata(db2_reports['itemid'][0])

meta[0].get('query')
# TODO: time to parse this query

meta = meta[0]
