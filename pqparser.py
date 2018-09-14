"""
parse M Scripts to verify which databases are being acessed

"""

import re

get_variables = re.compile('shared (\w+) = \"([\w.:]+)\"') # 2 groups, first group is variable name and the second is variable value
get_sources = re.compile('DB2\.Database\W*\((\w+)\W+(\w+)[\s\S]+?Query=\"([\s\S]+?)\"') # 3 groups, host variable, database variable, and Query executed

def has_db2_sources(itemid):
    file = open('input/metadata/'+itemid+'.m','r',encoding='utf-8').read()
    db2_sources = get_sources.findall(file)
    return len(db2_sources) > 0
