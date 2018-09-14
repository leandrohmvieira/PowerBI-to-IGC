#library to manage all IO operations with the Power Bi Report Server
import pyodbc
import pandas as pd
import os

class PbiServer:

    server = None
    database = None
    username = None
    password = None
    connection = None

    def __init__(self):
        self.server = os.getenv("SERVER")
        self.database = os.getenv("DATABASE")
        self.username = os.getenv("USER")
        self.password = os.getenv("PASSWORD")
        self.connection = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)

    def download_all_reports(self,repository):
        """
        Download all reports from pbi report server, by querying its BinaryContent from table catalogitemextendedcontent
        and saving its contents into a file.


        """
        all_reports_query = open('select_all_reports.sql', 'r').read()
        report_content_query = open('select_report_content.sql', 'r').read()
        reports = pd.read_sql_query(all_reports_query, self.connection)

        for report in reports.itertuples():
            print("Downloading {}".format(report.name))
            print("{}% completed".format(int(100 * float(report.Index+1)/float(reports.shape[0]))))
            os.sys.stdout.write('\r')
            #download report into reports Folder
            report_content = pd.read_sql_query(report_content_query,self.connection,params=[report.itemid])
            input_filename = repository.reports+report.itemid+".pbix"
            with open(input_filename, "wb") as pbix_file:
                pbix_file.write(report_content['BinaryContent'][0])
            pbix_file.close()
        del pbix_file
        del all_reports_query
        del report_content_query
        return None
    def get_report_list(self):
        all_reports_query = open('select_all_reports.sql', 'r').read()
        return pd.read_sql_query(all_reports_query, self.connection)
