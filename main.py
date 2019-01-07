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
#igc = igc()

# Step 1: truncate all objects (temporary)
#r = igc.delete_bundle()

# Step 2: Register bundle
#result = igc.register_bundle(repo)

# Step 3: Download Power BI db2_reports
#pbi.download_all_reports(repo)

# Step 4: Extract the M scripts of all reports
#repo.extract_pbi_queries()

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
    items = pd.DataFrame(list(items_list),columns=['item_table_schema','item_table_name','item_table_alias','item_name'])
    items['item_queryid'] = row.query_id
    #items['item_table_schema'] = items['item_table_name'].split('.')[0]
    item_rows.append(items)

items = pd.concat(item_rows)
items = items.reset_index(drop=True)

items = labeler.label_dataframe(items,field_prefix='item')

asset_tree = pd.merge(asset_tree,items,how='left',left_on='query_id',right_on='item_queryid')

# Step 6: Generate XML string with assets to be inserted
#xml_file = xml.new_asset_builder(asset_tree)

# Step 6: Generate XML string with assets to be inserted
#xml_file = xml.build_asset_xml(asset_tree)

# Step 7: Call asset insert request
#request = igc.insert_all_assets(xml_file)

#['folder_internal_id','report_internal_id','query_internal_id','item_internal_id']

#asset_tree[asset_tree['item_internal_id'].isin(['a950','a962'])][['folder_internal_id','report_internal_id','query_internal_id','item_internal_id']]

#asset_tree[asset_tree['item_internal_id'].isin(['a764','a787'])].filter(regex='item_')

#asset_tree[asset_tree['item_internal_id'].isin(['a950','a962'])]


# Step 8: Generate XML string with lineage Information

# To generate lineage information its necessary to build the entire database asset tree and label them with an internal_id, *sigh*


db_labeler = xml.id_generator(prefix='e')

def generate_db_ids(asset_tree,id_generator,field):

    field_frame = xml.search_df(asset_tree,field,dropna=True,dropon=field)
    field_frame = db_labeler.label_dataframe(field_frame,field)
    asset_tree = pd.merge(asset_tree,field_frame,how='left',left_on=field,right_on=field,suffixes=('','_database'))

    return asset_tree

#labeling database hosts

asset_tree = generate_db_ids(asset_tree,db_labeler,'query_host')

#labeling database instances

asset_tree = generate_db_ids(asset_tree,db_labeler,'query_database')

#labeling database schemas

asset_tree = generate_db_ids(asset_tree,db_labeler,'item_table_schema')

#labeling database tables

asset_tree = generate_db_ids(asset_tree,db_labeler,'item_table_name')

#labeling database columns

asset_tree = generate_db_ids(asset_tree,db_labeler,'item_name')


from lxml import etree

doc = etree.Element("doc",{"xmlns":"http://www.ibm.com/iis/flow-doc"})
#create assets
assets_level = etree.SubElement(doc,"assets")

#append all assets as children to the assets xml node
# assets_level = xml.append_host(assets_level,asset_tree,only_name=True)
# assets_level = xml.append_folders(assets_level,asset_tree,only_name=True)
# assets_level = xml.append_reports(assets_level,asset_tree,only_name=True)
# assets_level = xml.append_queries(assets_level,asset_tree,only_name=True)
#assets_level = xml.append_query_items(assets_level,asset_tree,only_name=True)
assets_level = xml.append_database_host(assets_level,asset_tree)
assets_level = xml.append_database_instances(assets_level,asset_tree)
assets_level = xml.append_database_schemas(assets_level,asset_tree)
assets_level = xml.append_database_tables(assets_level,asset_tree)
assets_level = xml.append_database_columns(assets_level,asset_tree)

#now with the assets appended, its time to declare their relationships

flow_level = etree.SubElement(doc,"flowUnits")

#lets try to build query items lineage



items = xml.search_df(asset_tree,"item_")
items = items[~items['item_internal_id'].isna()]
#create item assets
for idx,row in items.iterrows():
    flow_unit = etree.SubElement(flow_level,"flowUnit",{"assetID":row.item_internal_id})

    subFlow = etree.SubElement(flow_unit,"subFlows",{"flowType":"SYSTEM","comment":"grupo de linhagem da coluna "+row.item_name })

    subFlow_unit = etree.SubElement(subFlow,"flow",{"sourceIDs":row.item_name_internal_id,"targetIDs":row.item_internal_id,"comment":"unidade de linhagem da coluna "+row.item_name})

etree.tostring(doc,pretty_print=True)

#assets_level = append_folders(assets_level,asset_tree)
#assets_level = append_reports(assets_level,asset_tree)
#assets_level = append_queries(assets_level,asset_tree)
#assets_level = append_query_items(assets_level,asset_tree)
