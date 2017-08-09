from flask import Flask, render_template, jsonify, request, redirect, url_for

import sys

sys.path.append('../')
from model.eventstore import store_events, find_events
from model import Event, ORIGIN, generate_timestamp, generate_event, apply_events

app = Flask(__name__)

ENTITY_ID = 666


@app.before_first_request
def setup():
    store_single_event(ORIGIN)


def update_values(x, y):
    store_single_event(Event('jj', generate_timestamp(), x, y))


def store_single_event(event):
    store_events(ENTITY_ID, [event])


@app.route('/input/', methods=['POST'])
def put_data():
    x = int(request.form['x'])
    y = float(request.form['y'])

    print 'Got %d and %f' % (x, y)
    update_values(x, y)
    return redirect(url_for('index'))


def get_times():
    past_events = find_events(ENTITY_ID)
    return [e.ts for e in past_events]


@app.route('/data/', methods=['GET'])
@app.route('/data/<int:ts>', methods=['GET'])
def get_data(ts=0):
    past_events = find_events(ENTITY_ID)
    # if ts available filter
    if ts != 0:
        past_events = filter(lambda a: a.ts < ts, past_events)

    print('Events so far: %r' % past_events)
    entity = apply_events(past_events)

    # just for fun, by each retrieval we add a new Event
    if ts == 0:
        new_event = generate_event(past_events[-1])
        store_single_event(new_event)

    # transformation for plotting
    return jsonify({'x': [x for x in entity.keys()], 'y': [y for x, y in entity.items()], 'times': get_times()})


@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


app.run(host='0.0.0.0', port=8080, debug=True)
