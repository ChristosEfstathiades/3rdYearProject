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
        self.ns = Namespace("http://www.iana.org/assignments/relation/")
        self.graphs = []
        self.urls = [URI]
        self.depthLimit = 20
        self.visited = {URI}

    def crawl(self):
        counter = 0
        for url in self.urls: 
            if counter > self.depthLimit:
                break
            try:
                self.signposts = signposting.find_signposting_http(url) 
            except:
                print("Error: No HTTP signposting found")
                self.crawl_html(url)
            else:
                if len(self.signposts.signposts) > 0:
                    self.collect(url)
                else:
                    self.crawl_html(url)
            counter += 1
            self.visited.add(url)    

    def crawl_html(self, url): # TODO https://edp-portal.eurac.edu/discovery/b7db0a55-31ac-4339-bf60-a6124fb45915 has both http and html signposting that differ so maybe union
        try:
            self.signposts = signposting.find_signposting_html(url)
        except:
            print("Error: No HTML signposting found") 
        else:
            if len(self.signposts.signposts) > 0:
                print("html signposting found")
                self.collect(url)

    def collect(self, url):
        self.origin = url

        # Crawls level 1 typed links - HTTP
        signposts = self.collect_signposts(self.signposts)
        metadata = self.collect_metadata(self.signposts.describedBy)
        
        
        # Crawls level 2 typed links
        linksetData = self.linkset_handler(self.signposts.linksets)

        graphData = KG(self.origin, signposts, metadata, linksets=linksetData)
        self.graphs.append(graphData.get_kg())
        

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
                linkType = link.type # fix: links that have the wrong type declared - https://s11.no/2022/a2a-fair-metrics/11-http-describedby-iri-wrong-type/
                if link.type == None: # Some links have undefined types
                    linkType = util.guess_format(link.target)
                if linkType in self.describedByFormats:
                    RDFfile = link.target
                    try:
                        graph = Graph().parse(RDFfile, format=linkType)
                    except:
                        print("Failed to parse metadata") # content neg? https://s11.no/2022/a2a-fair-metrics/16-http-describedby-conneg/
                    else:
                        metadata[link.target] = graph
                else:
                    print("Parser does not accept format: " + linkType)
            return metadata
        else:
            return {}


    def linkset_handler(self, linksets):
        if len(linksets) > 0:
            linksetData = {}
            print("linkset(s) found")
            for linkset in linksets:
                try: 
                    linksetSignposts = signposting.find_signposting_linkset(linkset.target)
                except:
                    print("Couldn't parse linkset of type " + linkset.type)
                    # TODO some linksets arent getting parsed that should likely due to some profile stuff (application/linkset, application/linket+json) compare json files that work to ones that don't - whats the difference, try looking at rel/profile and use rdflib-ld
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
            return {}
                    

    def linksets(self, signposts, graph):
        for linkset in signposts.linksets:
            graph.add((self.subject(linkset), self.ns.linkset, URIRef(linkset.target)))
    
    def described_by(self, signposts, graph):
        for signpost in signposts.describedBy:
            graph.add((self.subject(signpost), self.ns.describedby, URIRef(signpost.target)))

    def cite_as(self, signposts, graph):
        if signposts.citeAs != None:
            graph.add((self.subject(signposts.citeAs), self.ns.citeas, URIRef(signposts.citeAs.target))) 
        else:
            print("No cite-as link at " + self.origin)

    def items(self, signposts, graph):
        for signpost in signposts.items:
            graph.add((self.subject(signpost), self.ns.item, URIRef(signpost.target))) 
            self.addURL(signpost.target) 
        

    def author(self, signposts, graph):
        for signpost in signposts.authors:
            graph.add((self.subject(signpost), self.ns.author, URIRef(signpost.target))) 
            self.addURL(signpost.target) # verify that URI is URL
        
    def licenses(self, signposts, graph):
        if signposts.license != None:
            graph.add((self.subject(signposts.license), self.ns.license, URIRef(signposts.license.target))) 
            self.addURL(signposts.license.target) # verify that URI is URL
        else:
            print("No license link at " + self.origin)

    def types(self, signposts, graph):
        for signpost in signposts.types:
            graph.add((self.subject(signpost), self.ns.type, URIRef(signpost.target)))

    def collection(self, signposts, graph):
        if signposts.collection != None:
            graph.add((self.subject(signposts.collection), self.ns.collection, URIRef(signposts.collection.target))) 
            self.addURL(signposts.collection.target) # verify that URI is URL using absoluteURI function
        else:
            print("No collection link at " + self.origin)

    def addURL(self, url):
        if url not in self.visited:
            self.urls.append(url)
            self.visited.add(url)

    def subject(self, signpost):
        if signpost.context != None:
            return URIRef(signpost.context)
        else:
            return URIRef(self.origin)

            