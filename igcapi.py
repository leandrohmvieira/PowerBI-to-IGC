"""
Python Wrapper around IBM Information Governance Catalog restful service
"""
import os
import requests

class igc:

    session = None
    base_url = 'https://glossario.intranet.bb.com.br:9443/ibm/iis/igc-rest/v1/'

    def __init__(self):
        s = requests.Session()
        s.proxies = {"http": os.getenv("PROXY_STRING") , "https": os.getenv("PROXY_STRING")}
        s.auth = (os.getenv("IGC_USER"),os.getenv("IGC_PASSWORD"))
        s.verify = False
        s.trust_env = False
        self.session = s
    def get_terms(self):
        types = 'term'
        payload = {'types':types}
        r = self.session.get(self.base_url+'search/',params = payload)
        # verify=False
        return r.text

# types = 'term'
# text = 'abatimento'
# search_properties = 'name'
#
#
# payload = {'types':types}
# r = self.session.get('https://glossario.intranet.bb.com.br:9443/ibm/iis/igc-rest/v1/search/',params = payload,verify=False)
# print(r.text)
# resultset = r.json()
# print(resultset)
# description = resultset.get('short_description')
# print(description)
# resultset = dict(r.text)
