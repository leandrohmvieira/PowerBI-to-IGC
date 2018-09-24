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
        # TODO: verify if our bundle exists on igc
        r = self.session.get(self.base_url+'bundles/')
        return 'PowerBI' in r.text

    def register_bundle(self,repository):
        # TODO: post zipped bundle onto igc
        files={'file': open(repository.bundle+'bundle.zip','rb')}
        return self.session.post(self.base_url+'bundles/',files= files)

    def insert_asset(self,asset):
        # TODO: well, dont know how to do it yet, open to suggestions
        r = self.session.post(self.base_url+'bundles/assets/',params = payload)
        return r.text

    def delete_bundle(self):
        if self.check_bundle():
            payload = {'id':'PowerBI'}
            r = self.session.delete(self.base_url+'bundles/PowerBI')
            return r
        else:
            return 'No bundle registered'

    def get_internal_id(self):
        self._internal_id += 1
        return 'a'+str(self._internal_id)

    def set_internal_id(self,value):
        self._internal_id = value

    @property
    def internal_id():
        doc = "The internal_id property, return a plus a number, incrementally"

        def fget(self):
            self._internal_id += 1
            return 'a'+str(self._internal_id)

        @internal_id.setter
        def fset(self, value):
            self._internal_id = value

        def fdel(self):
            del self._internal_id
        return locals()
    internal_id = property(**internal_id())
