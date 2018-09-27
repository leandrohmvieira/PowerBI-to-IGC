"""
Python Wrapper around IBM Information Governance Catalog restful service
"""
import os
import requests

class igc:

    session = None
    base_url = None
    _internal_id = None

    def __init__(self,proxy=False):
        s = requests.Session()
        if proxy:
            s.proxies = {"http": os.getenv("PROXY_STRING") , "https": os.getenv("PROXY_STRING")}

        s.auth = (os.getenv("IGC_USER"),os.getenv("IGC_PASSWORD"))
        s.verify = False
        s.trust_env = False
        self.session = s
        self.base_url = os.getenv("IGC_BASE_URL")
        self._internal_id = 0

    def get_terms(self):
        types = 'term'
        payload = {'types':types}
        r = self.session.get(self.base_url+'search/',params = payload)
        return r.text

    def check_bundle(self):
        r = self.session.get(self.base_url+'bundles/')
        return 'PowerBI' in r.text

    def register_bundle(self,repository):
        files={'file': open(repository.bundle+'bundle.zip','rb')}
        return self.session.post(self.base_url+'bundles/',files= files)

    def insert_all_assets(self,asset):
        headers={'content-type': 'application/xml'}
        r = self.session.post(self.base_url+'bundles/assets/',data = asset, headers=headers)
        return r

    def delete_bundle(self):
        if self.check_bundle():
            payload = {'id':'PowerBI'}
            r = self.session.delete(self.base_url+'bundles/PowerBI')
            return r
        else:
            return 'No bundle registered'

    #internal_id property, used to create a temporary id to all assets that going into XML
    def get_internal_id(self):
        self._internal_id += 1
        return 'a'+str(self._internal_id)

    def set_internal_id(self,value):
        self._internal_id = value

    internal_id = property(get_internal_id,set_internal_id)
