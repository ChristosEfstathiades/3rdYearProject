import signposting
from rdflib import Graph, URIRef, util, RDF, Literal, Namespace
from rdflib.namespace import FOAF
from kg import KG
class Crawler:
    def __init__(self, URI):
        self.origin = URI
        self.signposts = None
        self.describedByMetadata = Graph()
        self.describedByFormats = ["turtle", "application/ld+json", "text/turtle", "application/rdf+xml", "application/n-triples"] # application/json, application/xml
        # self.linksetFormats = ['application/linkset+json']
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
                    self.origin = self.urls[i]

                    # Crawls level 1 typed links - HTTP
                    signposts = self.collect_signposts(self.signposts)
                    metadata = self.collect_metadata(self.signposts.describedBy)
                    
                    
                    # Crawls level 2 typed links
                    linksetData = self.linkset_handler(self.signposts.linksets)

                    graphData = KG(self.origin, signposts, metadata, linksets=linksetData)
                    self.graphs.append(graphData)
        print(len(self.graphs))
                        
                    

        
            
        

    def collect_signposts(self, signposts):
        graph = Graph()
        self.cite_as(signposts, graph)
        self.items(signposts, graph)
        self.author(signposts, graph)
        self.licenses(signposts, graph)
        self.types(signposts, graph)
        self.collection(signposts, graph)
        self.linksets(signposts, graph)
        self.described_by(signposts, graph)
        if len(graph) > 0:
            return graph
        else:
            return None
    
    def collect_metadata(self, describedByLinks):
        if (len(describedByLinks) > 0):
            metadata = {}
            for link in describedByLinks:
                linkType = link.type # fix: links that have the wrong type declared
                if link.type == None: # Some links have undefined types
                    linkType = util.guess_format(link.target)
                if linkType in self.describedByFormats:
                    RDFfile = link.target
                    graph = Graph().parse(RDFfile, format=linkType)
                    metadata[link.target] = graph
                else:
                    print("Parser does not accept format: " + linkType)
            return metadata
        else:
            return None


    def linkset_handler(self, linksets):
        if len(linksets) > 0:
            linksetData = {}
            print("linkset(s) found")
            for linkset in linksets:
                try: 
                    linksetSignposts = signposting.find_signposting_linkset(linkset.target)
                except:
                    print(linkset.type)
                else:
                    sortedSignposts = signposting.Signposting(signposts = linksetSignposts.signposts)
                    signposts = self.collect_signposts(sortedSignposts)
                    metadata = self.collect_metadata(sortedSignposts.describedBy)
                    linksetData[linkset.target] = {
                        'signposts': signposts,
                        'metadata': metadata
                    }
            return linksetData
        else:
            return None
                    

    def linksets(self, signposts, graph):
        for linkset in signposts.linksets:
            graph.add((URIRef(self.origin), self.ns.linkset, URIRef(linkset.target)))
    
    def described_by(self, signposts, graph):
        for signpost in signposts.describedBy:
            graph.add((URIRef(self.origin), self.ns.types, URIRef(signpost.target)))
        

    def described_by_linksets(self, linkset):
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

    def cite_as(self, signposts, graph):
        if signposts.citeAs != None:
            graph.add((URIRef(self.origin), self.ns.citeas, URIRef(signposts.citeAs.target))) # change self.origin
        else:
            print("No cite-as link at " + self.origin)

    def items(self, signposts, graph):
        for signpost in signposts.items:
            graph.add((URIRef(self.origin), self.ns.item, URIRef(signpost.target))) 
        

    def author(self, signposts, graph):
        for signpost in signposts.authors:
            graph.add((URIRef(self.origin), self.ns.author, URIRef(signpost.target))) 
            self.urls.append(signpost.target) # verify that URI is URL
        
    def licenses(self, signposts, graph):
        if signposts.license != None:
            graph.add((URIRef(self.origin), self.ns.license, URIRef(signposts.license.target))) 
            self.urls.append(signposts.license.target) # verify that URI is URL
        else:
            print("No license link at " + self.origin)

    def types(self, signposts, graph):
        for signpost in signposts.types:
            graph.add((URIRef(self.origin), self.ns.types, URIRef(signpost.target)))

    def collection(self, signposts, graph):
        if signposts.collection != None:
            graph.add((URIRef(self.origin), self.ns.collection, URIRef(signposts.collection.target))) 
            self.urls.append(signposts.collection.target) # verify that URI is URL using absoluteURI function
        else:
            print("No collection link at " + self.origin)

    def test(self):
        return [self.signposts, self.signposts.signposts, self.signposts.context, self.signposts.other_contexts]
            