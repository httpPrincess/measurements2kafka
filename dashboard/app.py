from flask import Flask, render_template, jsonify, request, redirect, url_for
from math import sqrt
from random import uniform, random

app = Flask(__name__)


def next_step(x0, dt, stepnbr):
    return x0 + (0.5 - random()) * sqrt(dt) * uniform(0.0, stepnbr)


outx = list()
outy = list()


@app.before_first_request
def setup():
    outx.append(1)
    outy.append(5)


def update_values(x, y):
    global outx, outy
    if x in outx:
        ind = outx.index(x)
        outy[ind] = y


@app.route('/input/', methods=['POST'])
def put_data():
    x = int(request.form['x'])
    y = float(request.form['y'])

    print 'Got %d and %f' % (x, y)
    update_values(x, y)
    return redirect(url_for('index'))


@app.route('/data/', methods=['GET'])
def get_data():
    x = outx[-1]
    outx.append(x + 1)
    outy.append(next_step(x, 0.5, len(outx)))
    return jsonify({
        'x': outx,
        'y': outy})


@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


app.run(host='0.0.0.0', port=8080, debug=True)
