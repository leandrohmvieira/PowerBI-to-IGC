"""
Script which contains the main logic of the app, putting all together

The process consist of the following steps:

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
import pandas as pd
import xmlfactory as xml

#get environment variables from .env file
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#Create objects to manipulate the PbiServer, local repository and IGC rest api
pbi = powerapi.PbiServer()
repo = Repository()
igc = igc()

# Step 1: truncate all objects (temporary)
r = igc.delete_bundle()

# Step 2: Register bundle
result = igc.register_bundle(repo)

# Step 3: Download Power BI db2_reports
#pbi.download_all_reports(repo)

# Step 4: Extract the M scripts of all reports
#repo.extract_pbi_queries()

# Step 5: Generate a pandas dataframe for hosts, folders, reports and Queries

## TODO: internal_id generation must be moved to xmlfactory

###########################HOSTS##################
host = [{"name":os.getenv("SERVER"),
        "short_description":os.getenv("DATABASE"),
        "long_description":"",
        "$phase":"DEV",
        "internal_id":igc.internal_id
        }]
hosts = pd.DataFrame(host)
hosts.drop('internal_id',inplace=True,axis=1)## TODO: fix this shit later

##################FOLDERS#########################
folders = pbi.get_folder_list()

#create and populate a internal_id field, which is used to perform containment relationships
for idx,row in folders.iterrows():
    folders.at[idx,"internal_id"] = igc.internal_id


#getting internal_id from parent assets
#create a dataframe with folders that are parent
folders2 = folders[folders.itemid.isin(folders.parentid)]

#join child and father dataframes, to have both internal ids on a row
folders = folders.set_index('parentid').join(folders2.set_index('itemid'),rsuffix='_parent')
folders.parentid.fillna('',inplace=True)

##################REPORTS#########################
reports = pbi.get_report_list()

#create and populate a internal_id field, which is used to perform containment relationships
for idx,row in reports.iterrows():
    reports.at[idx,"internal_id"] = igc.internal_id

#join child and father dataframes, to have both internal ids on a row
reports = reports.set_index('parentid').join(folders.set_index('itemid'),rsuffix='_folder')
reports.reset_index(inplace=True)
folders.parentid.fillna('',inplace=True)

#################QUERIES##########################

reports['metadata'] = np.vectorize(pqp.get_metadata)(reports['itemid'])

metadata = reports.metadata.dropna().reset_index()

metadata_list = []
for row in metadata['metadata']:
    metadata_list.extend(row)

queries = pd.DataFrame(metadata_list)

for idx,row in queries.iterrows():
    queries.at[idx,"internal_id"] = igc.internal_id

#join child and father dataframes, to have both internal ids on a row
queries = queries.set_index('reportid').join(reports.set_index('itemid'),rsuffix='_report')
queries.reset_index(inplace=True)
#folders.parentid.fillna('',inplace=True)


# Step 6: Generate XML string with assets to be inserted
xml_file = xml.build_xml(host,hosts,folders,reports,queries)


# Step 7: Call asset insert request
request = igc.insert_all_assets(xml_file)
