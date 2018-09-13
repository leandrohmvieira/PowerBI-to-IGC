#import my libs
import powerapi
from repository import Repository

#import 3rd party libs
import glob
import zipfile
import subprocess
import shutil

#get environment variables from .env file
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#create a Power Bi Server connection and a local repository of files
pbi = powerapi.PbiServer()
repo = Repository()

#pbi.download_all_reports(repo)

for file in glob.glob(repo.reports+'*'):

    input_filename = file
    zip_ref = zipfile.ZipFile(input_filename, 'r')
    zip_ref.extractall('input/temp')
    zip_ref.close()
    #Unzipping the DataMashup file (yeah, PowerBI is all about zipped files)
    mashup_file = 'input/temp/DataMashup'
    sevenzip_path = os.getenv("7ZIP")
    source = mashup_file
    directory = '-oinput/temp' ## TODO: fix this -o thing

    #build and execute a 7zip call to unzip the DataMashup file
    cmd = [sevenzip_path, 'e', source , directory,'-aoa']
    sp = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    sp.wait()
    #to get the command output, use sp.communicate()
    #sp.communicate()
    ## TODO: Find a way to remove this 3rd party process dependence
    #get Section1.m file and move it to another folder
    shutil.move('input/temp/Section1.m', 'input/metadata/'+input_filename.split('\\')[1].split('.')[0]+'.m')
    repo.clear_temp()
