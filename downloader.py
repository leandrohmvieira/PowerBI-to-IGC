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

reports.head()
