from flask import Flask, request, render_template, url_for
from crawler import Crawler

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

@app.route("/")
def index():
    return render_template('index.html', error_msg=None)

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    if request.method == 'POST':
        url = request.form.get('url')
        debug = request.form.get('debug')


        crawled = Crawler(url)
        crawled.crawl()
        
        graphs = crawled.graphs
        print(str(len(graphs))+ " Graph(s) found")
        
        if len(graphs) == 0:
            return render_template('index.html', error_msg="Error: No signposting found")

        # graphs[0].serialize(format="xml", destination="./RDF/describedBy.rdf")

       
        if debug:
            q = """
            PREFIX ns: <http://www.iana.org/assignments/relation/>

            SELECT ?o
            WHERE {
                ?s ns:type ?o .
            }
            """
            abc = graphs[0]["signposts"].query(q)
            for row in abc:
                print(row)
            return render_template('debug.html', graphs = graphs)
        else:
            return render_template('crawled.html', graphs = graphs)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
