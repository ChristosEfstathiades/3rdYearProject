import signposting
from rdflib import Graph, URIRef, util, RDF, Literal
from rdflib.namespace import FOAF
class Crawler:
    def __init__(self, URI):
        self.origin = URI
        self.signposts = signposting.find_signposting_http(URI)
        self.describedBy = Graph()
        self.acceptedFormats = ["turtle", "application/ld+json", "text/turtle", "application/rdf+xml", "application/n-triples"] # application/json, application/xml
        self.linksetSignposts = None

    def crawl(self):
        if len(self.signposts.linksets) > 0:
            self.linkset_handler()
        
        self.described_by(self.signposts.describedBy)
        self.cite_as()
        self.items()
        self.author()
        self.licenses()
        

    def linkset_handler(self):
        print("linkset found")
        self.linksetDescribedBy = []
        print(self.signposts.linksets)
        # error handle linksets by type
        for linkset in self.signposts.linksets:
            print(linkset.target)
            self.linksetSignposts = signposting.find_signposting_linkset(linkset.target) # linksetSignposts should be array
            # for link in self.linksetSignposts:
            #     if link.rel == "describedby":
            #         self.linksetDescribedBy.append(link)

    
    def described_by(self, links):
        for link in links:
            linkType = link.type # fix: links that have the wrong type declared
            if link.type == None: # Some links have undefined types
                linkType = util.guess_format(link.target)
            if linkType in self.acceptedFormats:
                RDFfile = link.target
                g = Graph().parse(RDFfile, format=linkType)
                for sub, pred, obj in g:
                    self.describedBy.add((sub, pred, obj))
            else:
                print("Parser does not accept format: " + linkType)
                
    
    def cite_as(self):
        self.citeAs = self.signposts.citeAs

    def items(self):
        self.item = self.signposts.items

    def author(self):
        self.authors = self.signposts.authors
        
    def licenses(self):
        self.license = self.signposts.license