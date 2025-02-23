import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace
from rdflib.namespace import FOAF

# https://doi.org/10.34894/SRSB8I
depthLimit = 2
def crawlRecursion(url, depthLimit):
    if depthLimit == 0:
        return
    signposts = signposting.find_signposting_http(url)


ns = Namespace("https://www.iana.org/assignments/link-relations/")
print(ns.author)
graphs = []
urls = ["https://doi.org/10.34894/SRSB8I"]
def crawlLoop(i = 0):
    while i < 3:
        if len(urls) < i:
            break

        signposts = signposting.find_signposting_http(urls[i])
        kg = Graph()

        # handle linksets
        # handle signposts
        
        kg.add((URIRef(urls[i], ns.author, URIRef("https://ror.org/02rmd1t30"))))
        graphs.append(kg)
        urls.append("https://ror.org/02rmd1t30")
        i += 1

data = signposting.find_signposting_http("https://ror.org/02rmd1t30")
print(len(data.signposts))