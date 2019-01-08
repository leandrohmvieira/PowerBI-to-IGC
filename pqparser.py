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


"""
FUNCTION: get_metadata

input: Report ID(String)

output: A list of dicts containing the queries found into the referred Report, along with the source Host and Database

Description: Receives an itemid, go to file repository, reads the file with this id and parse sql queries inside it,
then returns the metadata found.
"""
def get_metadata(itemid):
    #only compatible with DB2 yet

    if has_db2_sources(itemid):
        #open report .m script
        file = open('input/metadata/'+itemid+'.m','r',encoding='utf-8').read()

        #Get host, database and queries from the .m script
        variables = dict(get_variables.findall(file))
        db2_sources = get_sources.findall(file)

        #build a list of dicts, each element is a dict with host, database and executed query(some roports have multiple queries)
        fields = ['query_host', 'query_database', 'query_content']
        metadata = [dict(zip(fields, source)) for source in db2_sources]

        #change the variables aliases to the real variables values
        for vars in metadata:
            vars.update({'query_host':variables.get(vars.get('query_host'))})
            vars.update({'query_database':variables.get(vars.get('query_database'))})
            vars.update({'query_reportid':itemid})
        return metadata
    else:
        return None

def parse_query(sql_str):

    # remove the /* */ comments
    q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", sql_str)

    # remove whole line -- and # comments
    lines = [line for line in q.splitlines() if not re.match("^\s*(--|#)", line)]

    # remove trailing -- and # comments
    q = " ".join([re.split("--|#", line)[0] for line in lines])

    # split on blanks, parens, semicolons, commas and operators
    tokens = re.split(r"[\s)(;,=<>]+", q)

    # scan the tokens. if we see a FROM or JOIN, we set the get_next
    # flag, and grab the next two tokens
    tables = []
    get_next = False
    get_alias = False
    for tok in tokens:
        if get_alias:
            tables.append((table,tok))
            get_alias = False
        elif get_next:
            if tok.lower() not in ["", "select"]:
                table = tok
                get_alias = True
                get_next = False
            else:
                get_next = False
        else:
            get_next = tok.lower() in ["from", "join"]
    #now with the tables and aliases from the query, we will get the aliased columns from the Query
    columns = set()
    for table in tables:
        tablename = table[0]
        alias = table[1]
        # TODO: Get tables from nested queries as well
        if '.' in tablename:
            for tok in tokens:
                if alias+"." in tok:
                    columns.add((tablename.split('.')[0],tablename,alias,tok.split(".")[1]))
                else:
                    continue
        else:
            continue

    #Transform tables into a table set, removing dynamic tables
    tables = set([i[0] for i in tables if '.' in i[0]])
    return columns,tables,tokens
# FIXME: the method above doesn't work when the last token is a unaliased table
