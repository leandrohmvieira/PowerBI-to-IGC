import requests
from requests.auth import HTTPProxyAuth

# request demo
# r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
# r.status_code
# r.headers['content-type']
# r.encoding
# r.text
# r.json()
#proxy auth https://stackoverflow.com/questions/13506455/how-to-pass-proxy-authentication-requires-digest-auth-by-using-python-requests

r = requests.get('https://glossario.intranet.bb.com.br:9443/ibm/iis/igc-rest/v1/metadata', proxies=proxies,auth=auth )


#https://glossario.intranet.bb.com.br:9443/ibm/iis/igc-rest/v1/search/?types=term&text=abatimento%20negocial&search-properties=name
