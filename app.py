from flask import Flask, request, render_template, url_for
from crawler import Crawler
from rdflib import Graph
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

@app.route("/")
def index():
    return render_template('index.html', error_msg=None)

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    if request.method == 'POST':
        url = request.form.get('url')
        debug = request.form.get('debug')
        labels = request.form.get('labels')


        crawled = Crawler(url)
        crawled.crawl()
        
        graphs = crawled.graphs
        print(str(len(graphs))+ " Graph(s) found")
        
        if len(graphs) == 0:
            return render_template('index.html', error_msg="Error: No signposting found")
        



        joint_signposts = Graph()
        provenances = []
        for graph in graphs:
            provenances.append(graph['provenance'])
            joint_signposts += graph['signposts']
            for linkset in graph['linksets']:
                joint_signposts += graph['linksets'][linkset]['signposts']
        joint_kg =  {
            'provenances': provenances,
            'signposts': joint_signposts
        }
        for s,p,o in joint_kg['signposts']:
            print(s,p,o)
        

        # graphs[0].serialize(format="xml", destination="./RDF/describedBy.rdf")

       
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
            return render_template('crawled.html', graphs = graphs, joint_kg = joint_kg, labels = labels)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
