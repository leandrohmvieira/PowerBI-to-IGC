import os
import glob
import zipfile
import subprocess
import shutil

class Repository:

    base = None
    reports = None
    metadata = None
    temp = None

    def __init__(self,path='input/'):
        self.base = path
        self.reports = path+'reports/'
        self.metadata = path+'metadata/'
        self.temp = path+'temp/'

    def clear_temp(self):
        files = glob.glob(self.temp+'**',recursive=True)
        for f in files:
            shutil.rmtree(f,ignore_errors=True)


    def clear_reports(self):
        files = glob.glob(self.reports+'**',recursive=True)
        for f in files:
            shutil.rmtree(f,ignore_errors=True)

    def clear_metadata(self):
        files = glob.glob(self.metadata+'**',recursive=True)
        for f in files:
            shutil.rmtree(f,ignore_errors=True)

    def extract_pbi_queries(self):

        for file in glob.glob(self.reports+'*'):

            input_filename = file
            zip_ref = zipfile.ZipFile(input_filename, 'r')
            zip_ref.extractall(self.temp)
            zip_ref.close()
            #Unzipping the DataMashup file (yeah, PowerBI is all about zipped files)
            sevenzip_path = os.getenv("7ZIP")
            source = self.temp+'DataMashup'
            directory = '-o'+self.temp

            #build and execute a 7zip call to unzip the DataMashup file
            cmd = [sevenzip_path, 'e', source , directory,'-aoa']
            sp = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            sp.wait()
            #to get the command output, use sp.communicate()
            #sp.communicate()
            ## TODO: Find a way to remove this 3rd party process dependence
            #get Section1.m file and move it to another folder
            shutil.move(self.temp+'Section1.m', self.metadata+input_filename.split('\\')[1].split('.')[0]+'.m')
            self.clear_temp()
