#import my libs
import powerapi
from repository import Repository
import parser

#get environment variables from .env file
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#create a Power Bi Server connection and a local repository of files
pbi = powerapi.PbiServer()
repo = Repository()

#pbi.download_all_reports(repo)
#repo.extract_pbi_queries()
