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

result.content

# Step 3: Download Power BI db2_reports
#pbi.download_all_reports(repo)

# Step 4: Extract the M scripts of all reports
#repo.extract_pbi_queries()

# Step 5: Generate a pandas dataframe for hosts, folders, reports and schemas

#host
host = [{"name":os.getenv("SERVER"),
        "short_description":os.getenv("DATABASE"),
        "long_description":"",
        "$phase":"DEV",
        "internal_id":igc.internal_id
        }]
hosts = pd.DataFrame(host)
hosts.drop('internal_id',inplace=True,axis=1)## TODO: fix this shit later

#folders
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

#reports
reports = pbi.get_report_list()

#create and populate a internal_id field, which is used to perform containment relationships
for idx,row in reports.iterrows():
    reports.at[idx,"internal_id"] = igc.internal_id

#join child and father dataframes, to have both internal ids on a row
reports = reports.set_index('parentid').join(folders.set_index('itemid'),rsuffix='_folder')
folders.parentid.fillna('',inplace=True)

from lxml import etree

#create doc
doc = etree.Element("doc",{"xmlns":"http://www.ibm.com/iis/flow-doc"})
#create assets
assets = etree.SubElement(doc,"assets")
#create host
asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiServer","repr":os.getenv("SERVER"),"ID":host[0]['internal_id']})
#create host attributes
for idx,series in hosts.iterrows():
    for column in series.keys():
        asset.append(etree.Element("attribute",{"name":column,"value":series[column]}))

#create folder assets
for idx,row in folders.iterrows():
    asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiFolder","repr":row['name'],"ID":row.internal_id})
    #create folder attributes
    asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
    #create containment reference
    if len(row.parentid) == 0:
        asset.append(etree.Element("reference",{"name":"$PbiServer","assetIDs":host[0]['internal_id']}))
    else:
        asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":row.internal_id_parent}))

#create report assets
for idx,row in reports.iterrows():
    asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiReport","repr":row['name'],"ID":row.internal_id})
    #create folder attributes
    asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
    #create containment reference
    asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":row.internal_id_folder}))


	# <headerSection>
	# 	<attribute localId="version" type="String" >
	# 		<label key="attr.PbiReport.version" inDefaultLocale="Version" />
	# 	</attribute>
	# </headerSection>
    #
	# <section>
	# 	<label key="section.PbiReport.Details" inDefaultLocale="Report Details" />
    #
	# 	<attribute localId="author" type="String">
	# 		<label key="attr.PbiReport.author" inDefaultLocale="Author" />
	# 	</attribute>
    #
	# </section>


#create importAction

importAction = etree.SubElement(doc,"importAction",{"partialAssetIDs":"a1"})



with open('output/generated.xml','wb') as f:
    f.write(etree.tostring(doc,pretty_print=True))

xml = etree.tostring(doc, pretty_print=True).decode('UTF-8')

request = igc.insert_all_assets(xml)

request.content
