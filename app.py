from flask import Flask, request, render_template, url_for
from crawler import Crawler
from rdflib import Graph
import requests
import urllib.parse

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
FUSEKI_STORE_URL = "http://localhost:3030/ds/data?graph="
FUSEKI_QUERY_URL = "http://localhost:3030/ds/query"

@app.route("/")
def index():
    URLs = fetchURLs()
    

    return render_template('index.html', error_msg=None, URLs = URLs)

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    if request.method == 'POST':
        url = request.form.get('url')
        debug = request.form.get('debug')
        labels = request.form.get('labels')
        edgecolor = request.form.get('edges')
        metadata = request.form.get('metadata')


        crawled = Crawler(url)
        crawled.crawl()
        
        graphs = crawled.graphs
        print(str(len(graphs))+ " Graph(s) found")
        
        if len(graphs) == 0:
            URLs = fetchURLs()
            return render_template('index.html', error_msg="Error: No signposting found", URLs = URLs)
        



        joint_signposts = Graph()
        metadata = Graph()
        provenances = []
        for graph in graphs:
            provenances.append(graph['provenance'])
            joint_signposts += graph['signposts']
            for linkset in graph['linksets']:
                joint_signposts += graph['linksets'][linkset]['signposts']
                for link in graph['linksets'][linkset]['metadata']:
                    metadata += graph['linksets'][linkset]['metadata'][link]
            for link in graph['metadata']:
                metadata += graph['metadata'][link]
            
        joint_kg =  {
            'provenances': provenances,
            'signposts': joint_signposts,
            'metadata': metadata
        }


        
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
            # q = """
            # PREFIX ns: <http://www.iana.org/assignments/relation/>

            # SELECT ?o
            # WHERE {
            #     ?s ns:type ?o .
            # }
            # """
            # abc = graphs[0]["signposts"].query(q)
            # for row in abc:
            #     print(row)
            return render_template('debug.html', graphs = graphs, joint_kg = joint_kg)
        else:
            return render_template('crawled.html', graphs = graphs, joint_kg = joint_kg, labels = labels, edgecolor=edgecolor, metadata=metadata)

@app.route('/fetch', methods=['GET'])
def fetch():
    url = request.args.get('url')
    encoded_graph_url = urllib.parse.quote(url, safe=':/')
    g = Graph()
    gres = g.query(
        f"""
        SELECT ?s ?p ?o WHERE {{
            SERVICE <{FUSEKI_QUERY_URL}> {{
                GRAPH <https://s11.no/2022/a2a-fair-metrics/15-http-describedby-no-conneg/> {{
                    ?s ?p ?o .
                    FILTER(STRSTARTS(STR(?p), "http://www.iana.org/assignments/relation/"))
                }}
            }}
        }}
        """
    )
    for row in gres:
        print(row.s, row.p, row.o)

@app.route('/store', methods=['POST'])
def store():
    if request.method == "POST":
        graph = request.form.get('graph')
        provenance = request.form.get('provenance')

        rdf = graph.serialize(format='turtle')

        headers = {"Content-Type": "text/turtle"}
        response = requests.post(FUSEKI_STORE_URL+provenance, data=rdf, headers=headers)
        if response.status_code in [200, 201]:
            print(1)
        else:
            print(2)
        
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
