from flask import Flask, request, render_template, url_for
import signposting

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
    
        ##Signposting crawl##
        s = signposting.find_signposting_http(url)
        # https://s11.no/2022/a2a-fair-metrics/01-http-describedby-only/
        ####

        return render_template('crawled.html', data=s)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)
