
#https://lxml.de/tutorial.html

import lxml.etree
import lxml.builder

E = lxml.builder.ElementMaker()
#element('value', anye params with commas)
#element('value',{dict with params})
DOC = E.doc
ASSETS = E.assets
ASSET = E.asset
ATTRIBUTE = E.attribute

the_doc = DOC(
                ASSETS(
                    ASSET( #cclass='$PowerBI-PbiServer',repr='Servidor Produção'
                        ATTRIBUTE({'name':'name', 'value':'Servidor Produção'})
                        )
                    ),xmlns='http://www.ibm.com/iis/flow-doc'
            )

print(lxml.etree.tostring(the_doc, pretty_print=True))
