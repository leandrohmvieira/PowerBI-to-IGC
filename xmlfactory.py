import os
from lxml import etree
import pandas as pd

def build_xml(host,hosts,folders,reports,queries):

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

    #create importAction

    importAction = etree.SubElement(doc,"importAction",{"partialAssetIDs":"a1"})



    with open('output/generated.xml','wb') as f:
        f.write(etree.tostring(doc,pretty_print=True))

    xml = etree.tostring(doc, pretty_print=True).decode('UTF-8')
    return xml
