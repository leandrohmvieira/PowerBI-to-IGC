class repository:

    path = None

    def __init__(self,path='input/'):
        self.path = path

    def clear_temp():
        files = glob.glob('input/temp/**')
        files
        for f in files:
            shutil.rmtree(f,ignore_errors=True)
