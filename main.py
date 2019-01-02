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
pbi.download_all_reports(repo)

# Step 4: Extract the M scripts of all reports
repo.extract_pbi_queries()

# Step 5: Generate a pandas dataframe for hosts, folders, reports, Queries and query items

#create id_generator object, which will label the assets. Necessary to build containment relationships
labeler = xml.id_generator()

##################HOST##################
host = pd.DataFrame([{"host_name":os.getenv("SERVER"),
        "host_short_description":os.getenv("DATABASE"),
        "host_long_description":"",
        "host_$phase":"DEV"
        }])

#add a internal_id to all rows
host = labeler.label_dataframe(host,field_prefix='host')

#hosts.drop('internal_id',inplace=True,axis=1)## TODO: fix this shit later
asset_tree = host

##################FOLDERS#########################
folders = pbi.get_folder_list()

#add a internal_id to all rows
folders = labeler.label_dataframe(folders,field_prefix='folder')

#getting internal_id from parent assets
#create a dataframe with folders that are parent
folders2 = folders[folders.folder_itemid.isin(folders.folder_parentid)]

#join child and father dataframes, to have both internal ids on a row
#folders = folders.set_index('parentid').join(folders2.set_index('itemid'),rsuffix='_parent')
folders_tree = pd.merge(folders,folders2,how='left',left_on='folder_parentid',right_on='folder_itemid',suffixes=('','_parent'))

folders_tree.folder_parentid.fillna('',inplace=True)

asset_tree = (
    folders_tree.assign(key=1)
    .merge(host.assign(key=1), on="key")
    .drop("key", axis=1))


##################REPORTS#########################
reports = pbi.get_report_list()

#add a internal_id to all rows
reports = labeler.label_dataframe(reports,field_prefix='report')

#join child and father dataframes, to have both internal ids on a row
#reports = reports.set_index('parentid').join(folders.set_index('itemid'),rsuffix='_folder')
#reports.reset_index(inplace=True)
#folders.parentid.fillna('',inplace=True)
asset_tree = pd.merge(reports,asset_tree,how='right',left_on='report_parentid',right_on='folder_itemid')

#################QUERIES##########################

#for each report, call the get_metadata fuction, to get query information from the .m scripts
reports['metadata'] = np.vectorize(pqp.get_metadata)(reports['report_itemid'])

#drop reports without queries from the queries dataframe
metadata = reports.metadata.dropna().reset_index()

#Join all lists from metadata column into a single list, then convert it into a dataframe
metadata_list = []
for row in metadata['metadata']:
    metadata_list.extend(row)

queries = pd.DataFrame(metadata_list)
queries = labeler.label_dataframe(queries,field_prefix='query')

#join child and father dataframes, to have both internal ids on a row
asset_tree = pd.merge(queries,asset_tree,how='right',left_on='query_reportid',right_on='report_itemid')
#queries = queries.set_index('reportid').join(reports.set_index('itemid'),rsuffix='_report')

#Since a report may have multiple queries, generate a query name, enumerating each report query (Asset name is a must on IGC)
#Also generating a query_id, since it does not have a native itemId from PowerBI
asset_tree.sort_values('report_itemid',inplace=True)

query_group = None
for idx,row in asset_tree[~asset_tree['query_content'].isna()].iterrows():
    if row.report_itemid != query_group:
        query_counter = 1
        query_group = row.report_itemid
        asset_tree.at[idx,'query_name'] = "Query "+row['report_name']+" "+str(query_counter)
        #row['query_name'] = "Query "+row['report_name']+" "+str(query_counter)
        asset_tree.at[idx,'query_id'] = idx
    else:
        query_counter += 1
        asset_tree.at[idx,'query_name'] = "Query "+row['report_name']+" "+str(query_counter)
        asset_tree.at[idx,'query_id'] = idx

#################QUERY ITEMS##########################

queries = xml.search_df(asset_tree,"query_")
queries = queries[~queries['query_internal_id'].isna()]

item_rows = []
for idx,row in queries.iterrows():

    items_list,_,_ = pqp.parse_query(row.query_content)
    items = pd.DataFrame(list(items_list),columns=['item_table_name','item_table_alias','item_name'])
    items['item_queryid'] = row.query_id
    item_rows.append(items)

items = pd.concat(item_rows)
items = items.reset_index(drop=True)

items = labeler.label_dataframe(items,field_prefix='item')

asset_tree = pd.merge(asset_tree,items,how='left',left_on='query_id',right_on='item_queryid')


# Step 6: Generate XML string with assets to be inserted
xml_file = xml.new_asset_builder(asset_tree)

# Step 6: Generate XML string with assets to be inserted
#xml_file = xml.build_asset_xml(asset_tree)

# Step 7: Call asset insert request
request = igc.insert_all_assets(xml_file)

#request.url

request.text

#['folder_internal_id','report_internal_id','query_internal_id','item_internal_id']

#asset_tree[asset_tree['item_internal_id'].isin(['a950','a962'])][['folder_internal_id','report_internal_id','query_internal_id','item_internal_id']]

#asset_tree[asset_tree['item_internal_id'].isin(['a764','a787'])].filter(regex='item_')

#asset_tree[asset_tree['item_internal_id'].isin(['a950','a962'])]

# Step 8: Generate XML string with lineage Information
#
# from lxml import etree
#
# #create doc
# doc = etree.Element("doc",{"xmlns":"http://www.ibm.com/iis/flow-doc"})
#
#
#
# #create assets section
# assets = etree.SubElement(doc,"assets")
#
# hosts
#
# #create host
# asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiServer","repr":os.getenv("SERVER"),"ID":host[0]['internal_id']})
# #append only the name attribute
# for idx,series in hosts.iterrows():
#         asset.append(etree.Element("attribute",{"name":"name","value":series['name']}))
#
#
# etree.tostring(doc)
# #create folder assets
# for idx,row in folders.iterrows():
#     asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiFolder","repr":row['name'],"ID":row.internal_id})
#     #create folder attributes
#     asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
#     #create containment reference
#     if len(row.parentid) == 0:
#         asset.append(etree.Element("reference",{"name":"$PbiServer","assetIDs":host[0]['internal_id']}))
#     else:
#         asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":row.internal_id_parent}))
#
# #create report assets
# for idx,row in reports.iterrows():
#     asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiReport","repr":row['name'],"ID":row.internal_id})
#     #create report attributes
#     asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
#     #create containment reference
#     asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":row.internal_id_folder}))
#
# #create query assets
# for idx,row in queries.iterrows():
#     asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiQuery","repr":row['name'],"ID":row.internal_id})
#     #create query attributes
#     asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
#     asset.append(etree.Element("attribute",{"name":"$query","value":row['query']}))
#     #create containment reference
#     asset.append(etree.Element("reference",{"name":"$PbiReport","assetIDs":row.internal_id_report}))
#
#
# #create importAction
# importAction = etree.SubElement(doc,"importAction",{"partialAssetIDs":"a1"})
#
#
#
# with open('output/generated.xml','wb') as f:
#     f.write(etree.tostring(doc,pretty_print=True))
#
# xml = etree.tostring(doc, pretty_print=True).decode('UTF-8')
#
#
# # Step 9: Call Lineage information registration
