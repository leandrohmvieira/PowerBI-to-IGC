# -*- coding: utf-8 -*-
"""
Very Ugly Script that ingest PowerBI Report Server files, parse the metadata undelying it
and finally, insert into OpenIGC API 
"""

import pyodbc
import pandas as pd
import zipfile

#Connect to PowerBI Report Server
server = '172.17.61.118' 
database = 'PBI_ReportServer' 
username = 'SQSIIS02' 
password = 'e08ihgas' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)



#Query that returns all reports on server (load to memory, beware!)
content_query = 'SELECT	CT.[Path]\
                ,CT.[Type]\
		          ,cc.ContentType\
                ,CONVERT(varbinary(max), cc.[Content]) AS BinaryContent\
                FROM dbo.[Catalog] AS CT\
		          LEFT OUTER JOIN dbo.CatalogItemExtendedContent cc\
        		        ON ct.ItemID = cc.ItemId\
                WHERE CT.[Type] IN (13) -- this indicates a PBI report\
                    cc.ContentType = "CatalogItem";'

#Query that returns a single report, for debug purposes
test_query = "select * from dbo.CatalogItemExtendedContent where ItemId = '12D071C9-81A8-4679-AA14-CFBF9E38C908' and ContentType = 'CatalogItem'"

#Load query result into pandas dataframe, because i want to
result = pd.read_sql(test_query, cnxn)

#writing pbix file onto disk
with open("pbiextracted.pbix", "wb") as fh:
    fh.write(result['Content'][0])


#cursor = cnxn.cursor()

#Uncompressing pbix file(the cat's jump is here, hehehe)
zip_ref = zipfile.ZipFile('pbiextracted.pbix', 'r')
zip_ref.extractall('pbiextracted')
zip_ref.close()





#cursor.execute("SELECT Name,Content from dbo.Catalog") 
#row = cursor.fetchone() 

#while row: 
#    print(row)
#    row = cursor.fetchone()