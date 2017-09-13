from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_bootstrap import Bootstrap
import sys

sys.path.append('../')
from model.kafkaeventstore import store_events, find_events, initialize_store
from model import Event, ORIGIN, generate_timestamp, apply_events, make_new_measurement

app = Flask(__name__)
Bootstrap(app)

ENTITY_ID = 666


def update_values(x, y):
    store_single_event(Event('jj', generate_timestamp(), x, y))


def store_single_event(event):
    store_events(ENTITY_ID, [event])


def get_times():
    past_events = find_events(ENTITY_ID)
    return [e.ts for e in past_events]


def split_data(entity):
    retx = list()
    rety = list()
    for x, y in sorted(entity.items()):
        retx.append(x)
        rety.append(y)

    return retx, rety


def get_authors():
    past_events = find_events(ENTITY_ID)
    return list({e.author for e in past_events})


@app.before_first_request
def setup():
    initialize_store(ENTITY_ID, ORIGIN)


@app.route('/input/', methods=['POST'])
def put_data():
    x = int(request.form['x'])
    y = float(request.form['y'])

    update_values(x, y)
    return redirect(url_for('index'))


@app.route('/data/', methods=['GET'])
@app.route('/data/<int:ts>', methods=['GET'])
def get_data(ts=0):
    past_events = find_events(ENTITY_ID)
    app.logger.debug(past_events)
    # if ts available filter
    if ts != 0:
        past_events = [e for e in past_events if e.ts < ts]

    entity = apply_events(past_events)

    # just for fun, by each retrieval we add a new Event
    if ts == 0:
        new_events = make_new_measurement(entity)
        entity = apply_events(new_events, entity)
        store_events(ENTITY_ID, new_events)

    # transformation for plotting
    vecx, vecy = split_data(entity)
    return jsonify(
        {
            'data': {
                'x': vecx,
                'y': vecy
            },
            'times': get_times(),
            'authors': get_authors()
        })


@app.route('/authors/', methods=['GET'])
@app.route('/authors/<author>', methods=['GET'])
def get_data_by_author(author=ORIGIN.author):
    past_events = find_events(ENTITY_ID)
    entity = apply_events([e for e in past_events if e.author == author])

    vecx, vecy = split_data(entity)
    return jsonify({
        "data": {'x': vecx,
                 'y': vecy
                 }
    })


@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


app.run(host='0.0.0.0', port=8080, debug=True)
