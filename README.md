# PowerBI-to-IGC
Simple Python app that connects to Power BI Report Server, crunch it's metadata and load it to IGC(IBM Information Governance Catalog)


## Application roadmap, so far:

* V0.1 -EXTREME GO HORSE EDITION, able to generate a CSV with generic reports to be imported by CSV bridge

* V0.2 - ULTRA EXTREME GO HORSE EDITION, able to extract and parse metadata from a .pbix file(but not generating any outputs, yet)

* V0.3(in progress) - Refactored and better structured code, which create a Power BI Bundle, Along with all reports from PBI report server

# How to use this Script(v0.1)

* First, if you haven't, [install ODBC Driver 13 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=53339)

* Also, if you haven't, [install 7-zip](https://www.7-zip.org/download.html)
  * 7-zip is needed to extract an specific zip file on the go, i'm looking on a way to get rid off this dependence

* Then, create a .env file on the project and fill it based on template.env


## update v0.3 (on dev phase, ON MASTER)

CSV bridge will be replaced by OpenIGC API
