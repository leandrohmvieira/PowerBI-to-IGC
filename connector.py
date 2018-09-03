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

#Load query result into pandas dataframe, because i want to
all_reports = open('select_all_reports.sql', 'r')
reports = pd.read_sql_query(all_reports.read(), cnxn)
#result.head()

#writing CSV compatible output file
output = open("output/bi_reports.csv","w",encoding='utf-8')

#Write the PowerBI Host
output.write("+++ BI Server - begin +++\n")
output.write("Name,Description\n")
output.write('server'+",\n")
output.write("+++ BI Server - end +++\n\n")

#defining a index of columns to fill the file
new_index = ['name','server','folder','description']

#Write PowerBI Reports
output.write("+++ BI Report - begin +++\n")
output.write("Name,Server,Folder,Description\n")
reports.to_csv(output,header=False,index=False,columns=reports.reindex(new_index)) #using reindex due to a future warning
output.write("+++ BI Report - end +++")
output.close()

reportid = reports['itemid'][0]




#writing pbix file onto disk - delayed to next release
#with open("pbiextracted.pbix", "wb") as fh:
#    fh.write(result['Content'][0])


#cursor = cnxn.cursor()

#Uncompressing pbix file(the cat's jump is here, hehehe) - delayed to next release
#zip_ref = zipfile.ZipFile('pbiextracted.pbix', 'r')
#zip_ref.extractall('pbiextracted')
#zip_ref.close()
