#this file have all communication methods between this application and pbi Report Server


def download_reports(reports):

    for report in reports.itertuples():
        #get report id and name
        reportid = report.itemid
        report_name = report.name

        print("Downloading {}".format(report.name))
        print("{}% completed".format(int(100 * float(report.Index+1)/float(reports.shape[0]))))
        os.sys.stdout.write('\r')
        #download report into reports Folder
        report_content = pd.read_sql_query(report_content_query,cnxn,params=[reportid])
        input_filename = "input/reports/"+report_name+".pbix"
        with open(input_filename, "wb") as pbix_file:
            pbix_file.write(report_content['BinaryContent'][0])
        pbix_file.close()
        del pbix_file
    return 1
