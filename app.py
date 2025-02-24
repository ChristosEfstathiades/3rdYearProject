from flask import Flask, request, render_template, url_for
from crawler import Crawler

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/greet/<name>')
def greet(name):
    return "hello " + name

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    if request.method == 'POST':
        url = request.form.get('url')

        # https://doi.org/10.34894/SRSB8I

        crawled = Crawler(url)
        crawled.crawl()
        data = crawled.test()
        
        graphs = crawled.graphs

        graphs[0].serialize(format="xml", destination="./RDF/describedBy.rdf")

       
        
        return render_template('crawled.html', graphs = graphs, data = data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
