"""
Python Wrapper around IBM Information Governance Catalog restful service
"""
import os
import requests

class igc:

    session = None
    base_url = None

    def __init__(self):
        s = requests.Session()
        s.proxies = {"http": os.getenv("PROXY_STRING") , "https": os.getenv("PROXY_STRING")}
        s.auth = (os.getenv("IGC_USER"),os.getenv("IGC_PASSWORD"))
        s.verify = False
        s.trust_env = False
        self.session = s
        self.base_url = os.getenv("IGC_BASE_URL")

    def get_terms(self):
        types = 'term'
        payload = {'types':types}
        r = self.session.get(self.base_url+'search/',params = payload)
        return r.text

    def check_bundle(self):
        # TODO: verify if our bundle exists on igc
        r = self.session.get(self.base_url+'bundles/')
        return 'PowerBI' in r.text

    def register_bundle(self,repository):
        # TODO: post zipped bundle onto igc
        file={'file': open(repository.bundle+'bundle.zip','rb')}
        return self.session.post(self.base_url+'bundles/',params = file)

    def insert_asset(self,asset):
        # TODO: well, dont know how to do it yet, open to suggestions
        r = self.session.post(self.base_url+'bundles/assets/',params = payload)
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
