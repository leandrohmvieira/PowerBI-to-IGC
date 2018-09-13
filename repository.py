import shutil
import glob

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
