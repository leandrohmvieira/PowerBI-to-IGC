
# TODO: organize this sh*t

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



output = open("output/database_sources.csv","w",encoding='utf-8')

#Write the database Host
output.write("+++ Host - begin +++\n")
output.write("Name,Description\n")
output.write(metadata[0]+",\n")
output.write("+++ Host - end +++\n\n")

#write database definitions
output.write("+++ Database - begin +++\n")
output.write("Name,Host,Description,Vendor,Version,Instance,Location,DBMS\n")
output.write(metadata[1]+","+metadata[0]+",\n")

## TODO: build a pandas dataframe with database definitions, or any another tabular writing to the file
output.write("+++ Database - end +++")


#write schema definitions
output.write("+++ Schema - begin +++\n")
output.write("Name,Host,Database,Description\n")
## TODO: build a pandas dataframe with schema definitions, or any another tabular writing to the file

output.write("+++ Schema - end +++")
output.close()

## TODO: evaluate if its possible to bring table level metadata to the dance floor
