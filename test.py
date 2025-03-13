import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace
from rdflib.namespace import FOAF

ns = Namespace("http://www.iana.org/assignments/relation/")
ns2 = Namespace("http://example.org/ns/")
g1 = Graph()
g1.add((URIRef("https://youtube.com"), ns.type, Literal(10)))
g1.add((URIRef("https://facebook.com"), ns2.type, Literal(10)))
g1.add((URIRef("https://rdflib.readthedocs.io/"), ns.item, Literal(10)))


q = """
PREFIX ns: <http://www.iana.org/assignments/relation/>

SELECT ?s ?p ?o WHERE {
  ?s ?p ?o .
  FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/"))
}
"""
abc = g1.query(q)
for row in abc:
    print(row.s)

# Merge metadata 
# Store metadata 
# Query iana predicates only

# PREFIX ns: <http://www.iana.org/assignments/relation/>

# SELECT ?s ?p ?o WHERE {
#   GRAPH <https://doi.pangaea.de/10.1594/PANGAEA.867908> {
#     ?s ?p ?o .
#   	FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/"))
#   }
# }