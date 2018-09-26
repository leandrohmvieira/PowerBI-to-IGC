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

# Step 5: Generate a pandas dataframe for hosts, folders, reports and schemas



#host
host = [{"name":os.getenv("SERVER"),
        "short_description":os.getenv("DATABASE"),
        "long_description":"",
        "phase":"DEV"
        }]
hosts = pd.DataFrame(host)

#folders
folders = pbi.get_folder_list()

#reports
reports = pbi.get_report_list()

from lxml import etree


#create doc
doc = etree.Element("doc",{"xmlns":"http://www.ibm.com/iis/flow-doc"})
#create assets
assets = etree.SubElement(doc,"assets")
#create asset
asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiServer","repr":"Servidor Produção","ID":igc.internal_id})

for row in hosts.iterrows():
    for column in row[1].keys():
        asset.append(etree.Element("attribute",{"name":column,"value":row[1][column]}))

request = igc.insert_all_assets(etree.tostring(doc))

request.headers
#
#
#
#
#
# # serie = row1[1]
# #
# # for column in serie.keys():
# #     print(column,serie[column])
# #
# #
# # <asset class="$PowerBI-PbiServer" repr="Servidor Produção" ID="a1">
# #   <attribute name="name" value="Servidor Produção"/>
# #   <attribute name="short_description" value="Servidor Produção 2"/>
# #   <attribute name="$phase" value="PROD"/>
# # </asset>
#
#
#
#
# #function applying methods:
# reports['db2'] = np.vectorize(pqp.has_db2_sources)(reports['itemid'])
# #reports['db2'] = reports['db2'].map(pqp.has_db2_sources)
#
# db2_reports = reports[reports.db2].reset_index()
#
# db2_reports['itemid'][0]
#
# meta = pqp.get_metadata(db2_reports['itemid'][0])
#
# meta
#
# query = meta[0].get('query')
#
# query_meta = pqp.get_query_from_tables.findall(query)
#
# query_meta
