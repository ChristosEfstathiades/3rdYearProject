import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace
from rdflib.namespace import FOAF
class Crawler:
    def __init__(self, URI):
        self.origin = URI
        self.signposts = None
        self.describedByMetadata = Graph()
        self.describedByFormats = ["turtle", "application/ld+json", "text/turtle", "application/rdf+xml", "application/n-triples"] # application/json, application/xml
        self.linksetFormats = ['application/linkset+json']
        self.linksetSignposts = None
        self.ns = Namespace("http://www.iana.org/assignments/relation/")
        self.graphs = []
        self.urls = [URI]#, "https://s11.no/2022/a2a-fair-metrics/34-http-item-rocrate/"]

    def crawl(self):
        for i in range(5): # TBC
            if len(self.urls) <= i:
                break
            # print(self.urls[i])
            try:
                self.signposts = signposting.find_signposting_http(self.urls[i]) 
            except:
                print("error") # add to this
            else:
                if len(self.signposts.signposts) > 0:
                    self.kg = Graph()
                    self.origin = self.urls[i]

                    # Stores level 1 typed links 
                    self.cite_as()
                    self.items()
                    self.author()
                    self.licenses()
                    self.types()
                    self.collection()
                    self.described_by()
                    if len(self.kg) > 0:
                        self.graphs.append(self.kg)

                    # Level 2 typed links
                    self.kg = Graph() # temporary solution, maybe change handler functions to be more generalised
                    self.linkset_handler()
                    if len(self.kg) > 0:
                        self.graphs.append(self.kg)

        
            
        

    def linkset_handler(self):
        if len(self.signposts.linksets) > 0:
            print("linkset(s) found")
            for linkset in self.signposts.linksets:
                try: 
                    self.linksetSignposts = signposting.find_signposting_linkset(linkset.target)
                except:
                    print(linkset.type)
                else:
                    self.signposts = signposting.Signposting(signposts = self.linksetSignposts.signposts)
                    self.cite_as()
                    self.items()
                    self.author()
                    self.licenses()
                    self.types()
                    self.collection()
                    self.described_by()
                    

    def described_by(self):
        for signpost in self.signposts.describedBy:
            self.kg.add((URIRef(self.origin), self.ns.describedby, URIRef(signpost.target)))   

            linkType = signpost.type # fix: links that have the wrong type declared
            if signpost.type == None: # Some links have undefined types
                linkType = util.guess_format(signpost.target)
            if linkType in self.describedByFormats:
                RDFfile = signpost.target
                g = Graph().parse(RDFfile, format=linkType)
                self.graphs.append(g)
                # for sub, pred, obj in g:
                #     self.kg.add((sub, pred, obj))
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

    def types(self):
        for signpost in self.signposts.types:
            self.kg.add((URIRef(self.origin), self.ns.types, URIRef(signpost.target)))

    def collection(self):
        if self.signposts.collection != None:
            self.kg.add((URIRef(self.origin), self.ns.collection, URIRef(self.signposts.collection.target))) 
            self.urls.append(self.signposts.collection.target) # verify that URI is URL using absoluteURI function
        else:
            print("No collection link at " + self.origin)

    def test(self):
        return [self.signposts, self.signposts.signposts, self.signposts.context, self.signposts.other_contexts]
            