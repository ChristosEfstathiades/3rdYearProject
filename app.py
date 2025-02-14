from flask import Flask, request, render_template, url_for
# import signposting
# from rdflib import Graph, URIRef, util, RDF, Literal
# from rdflib.namespace import FOAF
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
        ##Signposting crawl##
        
        
        # if len(s.signposts) == 0: #no signposting
        #     print("No http signposting found")
        #     s_html = signposting.find_signposting_html(url)
        #     linkElements = s_html
        #     print(linkElements.linksets)
        #     # s = s_html


        # if len(s.linksets) > 0:
        #     print("linkset found")
        #     for linkset in s.linksets:
        #         linkElements = signposting.find_signposting_linkset(linkset.target)
        #         print(len(linkElements.signposts))
        #     # what type of linkset? json? txt?
            
        # # describedByGraph = describedby(s.describedBy)
        # # for sub, pred, obj in describedByGraph:
        # #     kg.add((sub, pred, obj))

        # for link in s.items:
        #     formatGuess = util.guess_format(link.target)
        #     RDFfile = link.target
        #     print(link)
        #     # kg.add((URIRef(url), FOAF.Document, URIRef(link.target)))
        
        crawled = Crawler(url)
        crawled.crawl()
        kg = crawled.describedBy
        s = crawled.signposts
        linkElements = crawled.linksetSignposts

        kg.serialize(destination="./RDF/describedBy.ttl")
        
        return render_template('crawled.html', kg=kg, s=s, linkset=linkElements)
        # return render_template('crawled.html', s=s)

# def recursive_crawl(s):
    # for linkset in s.linksets:
    #     g = Graph()
    #     g.parse(linkset.target)
    #     for s, p, o in g:
    #         if s == URIRef()
    #         kg.add((s,p,o))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
