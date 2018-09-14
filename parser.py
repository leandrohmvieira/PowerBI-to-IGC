"""
parse M Scripts to verify which databases are being acessed

"""

import re

get_variables = re.compile('shared (\w+) = \"([\w.:]+)\"') # 2 groups, first group is variable name and the second is variable value
get_sources = re.compile('DB2\.Database\W*\((\w+)\W+(\w+)[\s\S]+?Query=\"([\s\S]+?)\"') # 3 groups, host variable, database variable, and Query executed
