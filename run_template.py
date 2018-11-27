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


# Step 3: Call asset insert request with insert template
xml_insert_file = open('templates/hello_world_insert.xml','rb').read()
request = igc.insert_all_assets(xml_insert_file)

# Step 4: Call asset lineage request with lineage template
xml_lineage_file = open('templates/hello_world_lineage.xml','rb').read()
request = igc.insert_lineage_data(xml_lineage_file)
