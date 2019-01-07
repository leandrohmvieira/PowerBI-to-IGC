import os
from lxml import etree
import pandas as pd

class id_generator:

    _internal_id = None
    _prefix = None

    def __init__(self,prefix='a'):

        self._internal_id = 0
        self._prefix = prefix

    #internal_id property, used to create a temporary id to all assets that going into XML
    def get_internal_id(self):
        self._internal_id += 1
        return self._prefix+str(self._internal_id)

    def set_internal_id(self,value):
        self._internal_id = value

    internal_id = property(get_internal_id,set_internal_id)

    def label_dataframe(self,dataframe,field_prefix=""):
        for idx,row in dataframe.iterrows():
            dataframe.at[idx,field_prefix+"_internal_id"] = self.internal_id
        return dataframe

def search_df(dataframe,regex,dropna=False,dropon=None):

    frame = dataframe.filter(regex=regex).drop_duplicates()

    if dropna:
        frame = frame[~frame[dropon].isna()]

    return frame


def append_host(parent_level,assets,only_name=False):

    #get host attributes from asset_tree
    host = search_df(assets,'^host_').reset_index(drop=True)

    #create host
    asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiServer","repr":host.at[0,'host_name'],"ID":host.at[0,'host_internal_id']})
    #create host attributes

    if only_name:
        for idx,row in host.iterrows():
            asset.append(etree.Element("attribute",{"name":"name","value":row.host_name}))

    else:
        host = host.drop('host_internal_id',axis=1)
        for idx,series in host.iterrows():
            for column in series.keys():
                asset.append(etree.Element("attribute",{"name":column.split('host_')[1],"value":series[column]}))

    return parent_level

def append_folders(parent_level,assets,only_name=False):

    #get folders attributes
    folders = search_df(assets,"folder_")

    #create folder assets
    for idx,row in folders.iterrows():
        asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiFolder","repr":row.folder_name,"ID":row.folder_internal_id})
        #create folder attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.folder_name}))
        #create containment reference

        #if a folder does not have a parent folder, then it's on root and must have it's host as parent
        if len(row.folder_parentid) == 0:
            asset.append(etree.Element("reference",{"name":"$PbiServer","assetIDs":assets.at[idx,'host_internal_id']}))
        else:
            asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":row.folder_internal_id_parent}))
    return parent_level

def append_reports(parent_level,assets,only_name=False):

    #get report attributes
    reports = search_df(assets,"report_",dropna=True,dropon='report_internal_id')
    #reports = reports[~reports['report_internal_id'].isna()]

    #create report assets
    for idx,row in reports.iterrows():
        asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiReport","repr":row.report_name,"ID":row.report_internal_id})
        #create report attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.report_name}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":assets.at[idx,"folder_internal_id"]}))
    return parent_level

def append_queries(parent_level,assets,only_name=False):

    #get report attributes
    queries = search_df(assets,"query_")
    queries = queries[~queries['query_internal_id'].isna()]

    #create query assets
    if only_name:
        for idx,row in queries.iterrows():
            asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiQuery","repr":row.query_name,"ID":row.query_internal_id})
            #create query attributes
            asset.append(etree.Element("attribute",{"name":"name","value":row.query_name}))
            #create containment reference
            asset.append(etree.Element("reference",{"name":"$PbiReport","assetIDs":assets.at[idx,'report_internal_id']}))
    else:
        for idx,row in queries.iterrows():
            asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiQuery","repr":row.query_name,"ID":row.query_internal_id})
            #create query attributes
            asset.append(etree.Element("attribute",{"name":"name","value":row.query_name}))
            asset.append(etree.Element("attribute",{"name":"$query","value":row.query_content}))
            #create containment reference
            asset.append(etree.Element("reference",{"name":"$PbiReport","assetIDs":assets.at[idx,'report_internal_id']}))
    return parent_level

def append_query_items(parent_level,assets,only_name=False):

    #get query items assets
    items = search_df(assets,"item_")
    items = items[~items['item_internal_id'].isna()]
    #create item assets
    for idx,row in items.iterrows():
        asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiQueryItem","repr":row.item_table_name+'.'+row.item_name,"ID":row.item_internal_id})
        #create item attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.item_table_name+'.'+row.item_name}))
        #asset.append(etree.Element("attribute",{"name":"$query","value":row.item_content}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiQuery","assetIDs":assets.at[idx,'query_internal_id']}))

    return parent_level

def append_database_host(parent_level,assets):

    db_host = search_df(assets,"query_host")
    db_host = db_host[~db_host['query_host'].isna()]

    for idx,row in db_host.iterrows():

        #remove port from host if it have one
        hostname = row.query_host.split(':')[0]

        asset = etree.SubElement(parent_level,"asset",{"class":"host","repr":hostname,"ID":row.query_host_internal_id})
        #create database host attributes
        asset.append(etree.Element("attribute",{"name":"name","value":hostname}))
    	# <asset class="host" repr="bdb2p04.plexbsb.bb.com.br" ID="e1">
		# 	<attribute name="name" value="bdb2p04.plexbsb.bb.com.br"/>
		# </asset>

    return parent_level

def append_database_instances(parent_level,assets):

    databases = search_df(assets,"query_database")
    databases = databases[~databases['query_database'].isna()]

    for idx,row in databases.iterrows():

        asset = etree.SubElement(parent_level,"asset",{"class":"database","repr":row.query_database,"ID":row.query_database_internal_id})
        #create database attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.query_database}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"host","assetIDs":assets.at[idx,'query_host_internal_id']}))

    return parent_level

def append_database_schemas(parent_level,assets):

    schemas = search_df(assets,"item_table_schema")
    schemas = schemas[~schemas['item_table_schema'].isna()]

    for idx,row in schemas.iterrows():

        asset = etree.SubElement(parent_level,"asset",{"class":"database_schema","repr":row.item_table_schema,"ID":row.item_table_schema_internal_id})
        #create schema attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.item_table_schema}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"database","assetIDs":assets.at[idx,'query_database_internal_id']}))

    return parent_level

def append_database_tables(parent_level,assets):

    tables = search_df(assets,"item_table_name")
    tables = tables[~tables['item_table_name'].isna()]

    for idx,row in tables.iterrows():

        asset = etree.SubElement(parent_level,"asset",{"class":"database_table","repr":row.item_table_name,"ID":row.item_table_name_internal_id})
        #create table attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.item_table_name}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"database_schema","assetIDs":assets.at[idx,'item_table_schema_internal_id']}))

    return parent_level

def append_database_columns(parent_level,assets):

    columns = search_df(assets,"item_name")
    columns = columns[~columns['item_name'].isna()]

    for idx,row in columns.iterrows():

        asset = etree.SubElement(parent_level,"asset",{"class":"database_column","repr":row.item_name,"ID":row.item_name_internal_id})
        #create columns attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.item_name}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"database_table","assetIDs":assets.at[idx,'item_table_name_internal_id']}))

    return parent_level

def new_asset_builder(asset_tree):

    #create doc
    doc = etree.Element("doc",{"xmlns":"http://www.ibm.com/iis/flow-doc"})
    #create assets
    assets_level = etree.SubElement(doc,"assets")

    #append all assets as children to the assets xml node
    assets_level = append_host(assets_level,asset_tree)
    assets_level = append_folders(assets_level,asset_tree)
    assets_level = append_reports(assets_level,asset_tree)
    assets_level = append_queries(assets_level,asset_tree)
    assets_level = append_query_items(assets_level,asset_tree)

    #create importAction
    importAction = etree.SubElement(doc,"importAction",{"partialAssetIDs":"a1"})

    with open('output/generated.xml','wb') as f:
        f.write(etree.tostring(doc,pretty_print=True))

    xml = etree.tostring(doc, pretty_print=True).decode('UTF-8')
    return xml
