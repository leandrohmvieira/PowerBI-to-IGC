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

#Load query result into pandas dataframe, because i feel like it
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

#defining a range of columns to fill the file
report_columns = ['name','server','folder','description']

#Write PowerBI Reports
output.write("+++ BI Report - begin +++\n")
output.write("Name,Server,Folder,Description\n")
reports[report_columns].to_csv(output,header=False,index=False) #using reindex due to a future warning
output.write("+++ BI Report - end +++")
output.close()


#get report id from the first report (dev purposes)
reportid = reports['itemid'][0]
report_name = reports['name'][0]
#open report id query
report_content_query = open('select_report_content.sql', 'r')
#execute the query with positional parameter: pyodbc does not support named parameters(today, 03/sep/2018)
report_content = pd.read_sql_query(report_content_query.read(),cnxn,params=[reportid])
#peeking the query result
report_content.head()

input_filename = "input/"+report_name+".pbix"
#writing pbix file onto disk - delayed to next release
with open(input_filename, "wb") as fh:
    fh.write(report_content['BinaryContent'][0])

#Unzipping pbix file(the cat's jump is here, hehehe)
zip_ref = zipfile.ZipFile(input_filename, 'r')
zip_ref.extractall('input/temp')
zip_ref.close()
#Unzipping the DataMashup file (yeah, PowerBI is a double zipped file)
mashup_file = 'input/temp/DataMashup.zip'
zip_ref = zipfile.ZipFile(mashup_file, 'r')
zip_ref.namelist()
zip_ref.infolist()
zip_ref.close()
