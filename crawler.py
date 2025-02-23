import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace
from rdflib.namespace import FOAF
class Crawler:
    def __init__(self, URI):
        self.origin = URI
        self.signposts = None
        self.describedBy = Graph()
        self.acceptedFormats = ["turtle", "application/ld+json", "text/turtle", "application/rdf+xml", "application/n-triples"] # application/json, application/xml
        self.linksetSignposts = None
        self.ns = Namespace("https://www.iana.org/assignments/link-relations/")

        self.graphs = []
        self.urls = [URI, "https://s11.no/2022/a2a-fair-metrics/34-http-item-rocrate/"]

    # def crawl(self):
    #     if len(self.signposts.linksets) > 0:
    #         self.linkset_handler()
        
    #     self.described_by(self.signposts.describedBy)
    #     self.cite_as()
    #     self.items()
    #     self.author()
    #     self.licenses()

    def crawl(self):
        i = 0
        while i < 5:
            if len(self.urls) <= i:
                break
            print(self.urls[i])
            try:
                self.signposts = signposting.find_signposting_http(self.urls[i]) # try statement
            except:
                print("error") # add to this
            else:
                if len(self.signposts.signposts) > 0:
                    self.kg = Graph()
                    self.origin = self.urls[i]

                    self.cite_as()
                    self.items()
                    self.author()
                    self.licenses()

                    self.graphs.append(self.kg)
            i += 1
            
        

    def linkset_handler(self):
        print("linkset found")
        self.linksetDescribedBy = []
        print(self.signposts.linksets)
        # error handle linksets by type
        for linkset in self.signposts.linksets:
            print(linkset.target)
            self.linksetSignposts = signposting.find_signposting_linkset(linkset.target) # linksetSignposts should be array
            

    
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
        if self.signposts.citeAs != None:
            self.kg.add((URIRef(self.origin), self.ns.citeas, URIRef(self.signposts.citeAs.target))) 
        else:
            print("No cite-as link at " + self.origin)

    def items(self):
        for signpost in self.signposts.items:
            self.kg.add((URIRef(self.origin), self.ns.item, URIRef(signpost.target))) 
        

    def author(self):
        for signpost in self.signposts.authors:
            self.kg.add((URIRef(self.origin), self.ns.author, URIRef(signpost.target))) 
            self.urls.append(signpost.target) # verify that URI is URL
        
    def licenses(self):
        if self.signposts.license != None:
            self.kg.add((URIRef(self.origin), self.ns.license, URIRef(self.signposts.license.target))) 
            self.urls.append(self.signposts.license.target) # verify that URI is URL
        else:
            print("No license link at " + self.origin)
            