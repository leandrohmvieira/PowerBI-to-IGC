# -*- coding: utf-8 -*-
"""
Very Ugly Script that ingest PowerBI Report Server files, parse the metadata undelying it
and finally, insert into OpenIGC API
"""

import pyodbc
import pandas as pd
import zipfile


#get environment variables from .env file
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#Connect to PowerBI Report Server
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
username = os.getenv("USER")
password = os.getenv("PASSWORD")

cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)


all_reports = open('select_all_reports.sql', 'r')

#Load query result into pandas dataframe, because i want to
result = pd.read_sql_query(all_reports.read(), cnxn)
#result.head()


#writing pbix file onto disk
#with open("pbiextracted.pbix", "wb") as fh:
#    fh.write(result['Content'][0])


#cursor = cnxn.cursor()

#Uncompressing pbix file(the cat's jump is here, hehehe) - delayed to next release
#zip_ref = zipfile.ZipFile('pbiextracted.pbix', 'r')
#zip_ref.extractall('pbiextracted')
#zip_ref.close()
