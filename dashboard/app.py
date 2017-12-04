from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_bootstrap import Bootstrap
import sys

sys.path.append('../')
from model.kafkaeventstore import store_events, find_events, initialize_store, select_snapshot, find_with_offset, \
    store_snapshot
from model import Event, ORIGIN, generate_timestamp, apply_events, make_new_measurement

app = Flask(__name__)
Bootstrap(app)

ENTITY_ID = 666
# 30 seconds between snapshot
SNAPSHOT_DELTA = 30000
SNAPSHOT_OFFSET_DELTA = 10


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
    generate_new = False
    if ts == 0:
        generate_new = True
        ts = generate_timestamp()

    entity, offset = select_snapshot(entity_id=ENTITY_ID, ts=ts)
    if entity:
        print('Got snapshot')

    past_events = sorted(find_with_offset(offset_low=offset), key=lambda e: e.value.ts)
    past_events = [e for e in past_events if (e.value.ts < ts and e.key == ENTITY_ID)]

    last_offset = past_events[-1].offset
    last_ts = past_events[-1].value.ts
    first_ts = past_events[0].value.ts

    entity = apply_events([e.value for e in past_events], entity=entity)

    if last_ts - first_ts > SNAPSHOT_DELTA:
        print('Saving snapshot {} -- {}'.format(last_ts, ts))
        store_snapshot(entity_id=ENTITY_ID, entity=entity, offset=last_offset, ts=last_ts)

    # just for fun, by each retrieval we add a new Event
    if generate_new:
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
