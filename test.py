import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace
from rdflib.namespace import FOAF

ns = Namespace("http://www.iana.org/assignments/relation/")
g1 = Graph()
g2 = Graph()
g1.add((URIRef("https://youtube.com"), ns.type, Literal(10)))
g2.add((URIRef("https://youtube.com"), ns.type, Literal(10)))
g2.add((URIRef("https://rdflib.readthedocs.io/"), ns.item, Literal(10)))
for s,p,o in g1:
    print(s,p,o)
for s,p,o in g2:
    print(s,p,o)

g1 += g2
for s,p,o in g1:
    print(s,p,o)
