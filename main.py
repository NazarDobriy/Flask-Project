from flask import Flask, render_template
from werkzeug.serving import run_simple

app = Flask(__name__)


@app.route('/api/v1/hello-world-6')
def hello_world():
    # return "Hello World! Варіант 6"
    return render_template("index.html")


server = run_simple('localhost', 5000, app, use_reloader=True)
