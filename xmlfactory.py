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

def search_df(dataframe,regex):
    return dataframe.filter(regex=regex).drop_duplicates()

def append_host(parent_level,assets):

    #get host attributes from asset_tree
    host = search_df(assets,'^host_').reset_index(drop=True)

    #create host
    asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiServer","repr":host.at[0,'host_name'],"ID":host.at[0,'host_internal_id']})
    #create host attributes
    host = host.drop('host_internal_id',axis=1)
    for idx,series in host.iterrows():
        for column in series.keys():
            asset.append(etree.Element("attribute",{"name":column.split('host_')[1],"value":series[column]}))
    return parent_level

def append_folders(parent_level,assets):

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

def append_reports(parent_level,assets):

    #get report attributes
    reports = search_df(assets,"report_")
    reports = reports[~reports['report_internal_id'].isna()]

    #create report assets
    for idx,row in reports.iterrows():
        asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiReport","repr":row.report_name,"ID":row.report_internal_id})
        #create report attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.report_name}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":assets.at[idx,"folder_internal_id"]}))
    return parent_level

def append_queries(parent_level,assets):

    #get report attributes
    queries = search_df(assets,"query_")
    queries = queries[~queries['query_internal_id'].isna()]

    #create query assets
    for idx,row in queries.iterrows():
        asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiQuery","repr":row.query_name,"ID":row.query_internal_id})
        #create query attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.query_name}))
        asset.append(etree.Element("attribute",{"name":"$query","value":row.query_content}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiReport","assetIDs":assets.at[idx,'report_internal_id']}))
    return parent_level

def append_query_items(parent_level,assets):

    #get query items assets
    items = search_df(assets,"item_")
    items = items[~items['item_internal_id'].isna()]
    #create item assets
    for idx,row in items.iterrows():
        asset = etree.SubElement(parent_level,"asset",{"class":"$PowerBI-PbiQueryItem","repr":row.item_name,"ID":row.item_internal_id})
        #create item attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row.item_name}))
        #asset.append(etree.Element("attribute",{"name":"$query","value":row.item_content}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiQuery","assetIDs":assets.at[idx,'query_internal_id']}))

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


def build_asset_xml(host,hosts,folders,reports,queries,columns):

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
        #create report attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiFolder","assetIDs":row.internal_id_folder}))

    #create query assets
    for idx,row in queries.iterrows():
        asset = etree.SubElement(assets,"asset",{"class":"$PowerBI-PbiQuery","repr":row['name'],"ID":row.internal_id})
        #create query attributes
        asset.append(etree.Element("attribute",{"name":"name","value":row['name']}))
        asset.append(etree.Element("attribute",{"name":"$query","value":row['query']}))
        #create containment reference
        asset.append(etree.Element("reference",{"name":"$PbiReport","assetIDs":row.internal_id_report}))


    #create importAction
    importAction = etree.SubElement(doc,"importAction",{"partialAssetIDs":"a1"})

    with open('output/generated.xml','wb') as f:
        f.write(etree.tostring(doc,pretty_print=True))

    xml = etree.tostring(doc, pretty_print=True).decode('UTF-8')
    return xml
