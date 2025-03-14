from flask import Flask, jsonify, request, render_template, url_for
from crawler import Crawler
from rdflib import Graph, URIRef
import requests
import urllib.parse

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
FUSEKI_STORE_URL = "http://localhost:3030/ds/data?graph="
FUSEKI_QUERY_URL = "http://localhost:3030/ds/query"

@app.route("/")
def index():
    URLs = fetchURLs() # fetch stored graphs

    return render_template('index.html', error_msg=None, URLs = URLs)

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    if request.method == 'POST':
        url = request.form.get('url')
        debug = request.form.get('debug')
        labels = request.form.get('labels')
        edgecolor = request.form.get('edges')
        displaymetadata = request.form.get('metadata')

        crawled = Crawler(url)
        crawled.crawl()
        
        graphs = crawled.graphs
        print(str(len(graphs))+ " Graph(s) found")
        
        if len(graphs) == 0:
            URLs = fetchURLs()
            return render_template('index.html', error_msg="Error: No signposting found", URLs = URLs)
        



        joint_signposts = Graph()
        metadata = Graph()
        metadataAdded = set()
        provenances = []

        # Joins each individual graph into joint knowledge graph
        # Selects first metadata found to prevent blank node duplication bug
        for graph in graphs:
            metadataLength = len(metadata)
            provenances.append(graph['provenance'])
            joint_signposts += graph['signposts']
            for linkset in graph['linksets']:
                joint_signposts += graph['linksets'][linkset]['signposts']
            for link in graph['metadata']:
                if bool(graph['metadata'][link]) and link not in metadataAdded:
                    metadata += graph['metadata'][link]
                    metadataAdded.add(link)
                    break
            if len(metadata) == metadataLength:
                for linkset in graph['linksets']: 
                    for link in graph['linksets'][linkset]['metadata']:
                        if bool(graph['linksets'][linkset]['metadata'][link]) and link not in metadataAdded:
                            metadata += graph['linksets'][linkset]['metadata'][link]
                            metadataAdded.add(link)
                            break
        # print(len(metadata))

            
        # metadata.serialize(destination="test.rdf", format="xml")
        joint_kg =  {
            'provenances': provenances,
            'signposts': joint_signposts,
            'metadata': metadata
        }

        # check if graph exists
        query = f"""
        ASK WHERE {{
            GRAPH <{joint_kg['provenances'][0]}> {{ ?s ?p ?o }}
        }}
        """
        params = {"query": query, "format": "json"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(FUSEKI_QUERY_URL, data=params, headers=headers)

        if response.status_code != 200:
            print("check if exist query failed")

        exists = response.json().get("boolean", False)
        if not exists:
            # stores graph
            graph = joint_kg['metadata'] + joint_kg['signposts']
            rdf = graph.serialize(format='turtle')

            headers = {"Content-Type": "text/turtle"}
            response = requests.post(FUSEKI_STORE_URL+joint_kg['provenances'][0], data=rdf, headers=headers)
            if response.status_code in [200, 201]:
                print("Succesfully stored graph")
            else:
                URLs = fetchURLs()
                return render_template('index.html', error_msg="Error: Could not store graph", URLs = URLs)
        

        if debug:
            return render_template('debug.html', graphs = graphs, joint_kg = joint_kg)
        else:
            return render_template('crawled.html', graphs = graphs, joint_kg = joint_kg, labels = labels, edgecolor=edgecolor, displaymetadata=displaymetadata)

@app.route('/fetch', methods=['GET'])
def fetch():
    url = request.args.get('url')
    g = Graph()
    # only fetches signposts and not metadata
    q = f"""
        SELECT ?s ?p ?o FROM <{url}> WHERE {{
            ?s ?p ?o .
            FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/"))
        }}
    """
    params = {
        "query": q,
        "format": "json"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(FUSEKI_QUERY_URL, data=params, headers=headers)
    
    data = response.json()

    for binding in data['results']['bindings']:
        g.add((URIRef(binding["s"]["value"]), URIRef(binding["p"]["value"]), URIRef(binding["o"]["value"])))
   

    joint_kg =  {
            'provenances': [url],
            'signposts': g
    }
    
    return render_template('crawled.html', graphs = None, joint_kg = joint_kg, labels = False, edgecolor=True, displaymetadata=False)
    

        
def fetchURLs():
    g = Graph()
    qres = g.query(
        f"""
        SELECT DISTINCT ?g
        WHERE {{
        SERVICE <{FUSEKI_QUERY_URL}> {{
            {{ GRAPH ?g {{ ?s ?p ?o }} }}
        }}
        }}
        LIMIT 50
        """
    )
    URLs = []
    for row in qres:
        URLs.append(row.g)
    return URLs

@app.route('/subgraph', methods=['POST'])
def subgraph():
    print(1)
    subgraph = request.form.get('subgraph')
    graph = request.form.get('graph')
    metadata = request.form.get('metadata')
    g = Graph()
    if metadata:
        q = f"""
            SELECT ?s ?p ?o WHERE {{
            GRAPH <{graph}> {{  
                ?s ?p ?o .
                FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/")) .
                FILTER(CONTAINS(STR(?s), "{subgraph}")) .
            }}
        }}
        """
    else:
        q = f"""
            SELECT ?s ?p ?o WHERE {{
            GRAPH <{graph}> {{  
                ?s ?p ?o .
                FILTER(CONTAINS(STR(?s), "{subgraph}")) .
            }}
        }}
        """

    params = {
        "query": q,
        "format": "json"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(FUSEKI_QUERY_URL, data=params, headers=headers)
    
    data = response.json()

    for binding in data['results']['bindings']:
        g.add((URIRef(binding["s"]["value"]), URIRef(binding["p"]["value"]), URIRef(binding["o"]["value"])))

    joint_kg =  {
            'provenances': [subgraph],
            'signposts': g
    }
    # for s,p,o in g:
    #     print(s,p,o)
    return render_template('crawled.html', graphs = None, joint_kg = joint_kg, labels = False, edgecolor=True, displaymetadata=metadata)
    

@app.route('/predicate', methods=['POST'])
def predicate():
    print(1)
    predicate = request.form.get('predicate')
    graph = request.form.get('graph')
    
    g = Graph()
    q = f"""
        PREFIX ns: <http://www.iana.org/assignments/relation/>
        SELECT ?s ?p ?o WHERE {{
        GRAPH <{graph}> {{  
            ?s ns:{predicate} ?o .
        }}
    }}
    """
       

    params = {
        "query": q,
        "format": "json"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(FUSEKI_QUERY_URL, data=params, headers=headers)
    
    data = response.json()

    for binding in data['results']['bindings']:
        g.add((URIRef(binding["s"]["value"]), URIRef("http://www.iana.org/assignments/relation/"+predicate), URIRef(binding["o"]["value"])))

    joint_kg =  {
            'provenances': [graph],
            'signposts': g
    }
    for s,p,o in g:
        print(s,p,o)
    return render_template('crawled.html', graphs = None, joint_kg = joint_kg, labels = False, edgecolor=True, displaymetadata=False)
    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
