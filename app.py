from flask import Flask, request, render_template, url_for
from crawler import Crawler
from rdflib import Graph
import requests
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
FUSEKI_STORE_URL = "http://localhost:3030/main/data?graph="
FUSEKI_QUERY_URL = "http://localhost:3030/main/query"

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


        crawled = Crawler(url)
        crawled.crawl()
        
        graphs = crawled.graphs
        print(str(len(graphs))+ " Graph(s) found")
        
        if len(graphs) == 0:
            URLs = fetchURLs()
            return render_template('index.html', error_msg="Error: No signposting found", URLs = URLs)
        



        joint_signposts = Graph()
        provenances = []
        for graph in graphs:
            provenances.append(graph['provenance'])
            joint_signposts += graph['signposts']
            for linkset in graph['linksets']:
                joint_signposts += graph['linksets'][linkset]['signposts']
            # for data in graph['metadata']:
            #     joint_signposts += graph['metadata'][data]
            
        joint_kg =  {
            'provenances': provenances,
            'signposts': joint_signposts
        }

        

        rdf = joint_kg['signposts'].serialize(format='turtle')

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
            return render_template('crawled.html', graphs = graphs, joint_kg = joint_kg, labels = labels, edgecolor=edgecolor)


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
        """
        SELECT DISTINCT ?g
        WHERE {
        SERVICE <http://localhost:3030/main/query> {
            { GRAPH ?g { ?s ?p ?o } }
        }
        }
        LIMIT 10
        """
    )
    URLs = []
    for row in qres:
        URLs.append(row.g)
    return URLs

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
