



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
