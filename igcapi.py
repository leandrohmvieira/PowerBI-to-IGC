"""
Python Wrapper around IBM Information Governance Catalog restful service
"""
import os
import requests

class igc:

    session = None
    base_url = None
    _internal_id = None

    def __init__(self):
        s = requests.Session()
        proxy = os.getenv("PROXY_ENABLED")
        if proxy == '1':
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

    def insert_lineage_data(self,lineage):
        headers={'content-type': 'application/xml'}
        r = self.session.post(self.base_url+'flows/upload/',data = lineage, headers=headers)
        return r
