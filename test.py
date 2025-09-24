import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace, BNode
from rdflib.namespace import FOAF

# s = signposting.find_signposting_http_link("https://repository.dri.ie/linkset/vm41bk02f/lset")
# print(s)

ns = Namespace("http://www.iana.org/assignments/relation/")
ns2 = Namespace("http://example.org/ns/")
g1 = Graph()
node = BNode()
g1.add((URIRef("https://youtube.com"), ns.type, node))
g1.add((URIRef("https://facebook.com"), ns2.type, BNode()))
g1.add((URIRef("https://rdflib.readthedocs.io/"), ns.item, Literal(10)))
g1.add((node, ns.item, Literal(10)))
node2 = BNode()
g2 = Graph()
g2.add((URIRef("https://youtube.com"), ns.type, node2))
g2.add((URIRef("https://facebook.com"), ns2.type, BNode()))
g2.add((URIRef("https://rdflib.readthedocs.io/"), ns.item, Literal(10)))
g2.add((node2, ns.item, Literal(10)))
g3 = Graph().parse("https://www.youtube.com/watch?v=90YdQHjjieg")
print(len(g3))


def find_equivalent_blank_nodes(g1, g2):
    """
    Finds blank nodes in g2 that match blank nodes in g1 based on predicates and values.
    Returns a mapping of g2's blank nodes to g1's blank nodes.
    """
    mapping = {}
    
    for bnode_g1 in g1.subjects():
        if isinstance(bnode_g1, BNode):
            for bnode_g2 in g2.subjects():
                if isinstance(bnode_g2, BNode):
                    # Compare predicates and objects
                    triples_g1 = set(g1.predicate_objects(bnode_g1))
                    triples_g2 = set(g2.predicate_objects(bnode_g2))
                    
                    if triples_g1 == triples_g2:
                        mapping[bnode_g2] = bnode_g1  # Map equivalent blank nodes
                        break
    return mapping


# bnode_mapping = find_equivalent_blank_nodes(g1, g2)
# print(bnode_mapping)
# for s, p, o in g2:
#     new_s = bnode_mapping.get(s, s)  # Replace blank nodes if found in mapping
#     new_o = bnode_mapping.get(o, o)
#     g1.add((new_s, p, new_o))  # Merge into g1

# for s,p,o in g1:
#     print(s,p,o)
# q = """
# PREFIX ns: <http://www.iana.org/assignments/relation/>

# SELECT ?s ?p ?o WHERE {
#   ?s ?p ?o .
#   FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/"))
# }
# """
# abc = g1.query(q)
# for row in abc:
#     print(row.s)

# Merge metadata 
# Store metadata 
# Query iana predicates only

# PREFIX ns: <http://www.iana.org/assignments/relation/>

# SELECT ?s ?p ?o WHERE {
#     ?s ?p ?o .
#   	FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/"))
# }