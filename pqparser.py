"""
parse M Scripts to verify which databases are being acessed

"""

import re

get_variables = re.compile('shared (\w+) = \"([\w.:]+)\"') # 2 groups, first group is variable name and the second is variable value
get_sources = re.compile('DB2\.Database\W*\((\w+)\W+(\w+)[\s\S]+?Query=\"([\s\S]+?)\"') # 3 groups, host variable, database variable, and Query executed
get_query_from_tables = re.compile('FROM\s+(\w+)\.(\w+)') # 2 groups, schema and name of all tables right after a FROM keyword
get_query_join_tables = re.compile('JOIN\s+(\w+)\.(\w+)') # 2 groups, schema and name of all tables right after a JOIN keyword

def has_db2_sources(itemid):
    try:
        file = open('input/metadata/'+itemid+'.m','r',encoding='utf-8').read()
        db2_sources = get_sources.findall(file)
        return len(db2_sources) > 0
    except IOError as e:
        return None

def get_metadata(itemid):
    if has_db2_sources(itemid):
        file = open('input/metadata/'+itemid+'.m','r',encoding='utf-8').read()
        variables = dict(get_variables.findall(file))
        db2_sources = get_sources.findall(file)
        fields = ['host', 'database', 'query']
        metadata = [dict(zip(fields, source)) for source in db2_sources]
        for vars in metadata:
            vars.update({'host':variables.get(vars.get('host'))})
            vars.update({'database':variables.get(vars.get('database'))})
            vars.update({'reportid':itemid})
        return metadata
    else:
        return None
