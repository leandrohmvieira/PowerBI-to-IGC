# PowerBI-to-IGC

This Application aims to extract metadata from Power BI reports and represent it on Information Governance Catalog, using the OpenIgc rest api.

## Bundle definition

The Power BI bundle hierarchy is defined as:

* Power BI Server
  * Power BI Folder
    * Power BI Folder(Folder is a self containable class)
      * Power BI Report
        * Power BI Query
          * Power BI Query Item


## How to use this Application

This app is still on development and is not ready to production environment yet, if you want to give it a go, please get a release package, not the last from master.

# Using this application:

* First, if you haven't, [install ODBC Driver 13 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=53339)

* Also, if you haven't, [install 7-zip](https://www.7-zip.org/download.html)
  * 7-zip is needed to extract an specific zip file on the go

* Then, create a .env file on the project and fill it based on template.env

## Application roadmap, so far:

* V0.1 - CSV generator which generate a csv file that contains the host, folders and reports, ready to be imported by IGC CSV bridge

* V0.2 - Application will register a bundle on OpenIGC, and will add all folders and reports under the custom bundle

* V0.3 - Ability to ingest and show queries from power BI made on DB2 only

* V0.4 - App able to get metadata at column level from queries, but column naming still a little wonky though

* V0.5(DEV) - Data Lineage support

## Contributing

This is a open source project and i welcome any contributions, please feel free to reach me at leandrohmvieira@gmail.com if you want to join this project
