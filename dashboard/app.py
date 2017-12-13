from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_bootstrap import Bootstrap

from model.kafkaeventstore import store_events, find_events, initialize_store, select_snapshot, \
    store_snapshot, get_offsets
from model import Event, ORIGIN, generate_timestamp, apply_events, make_new_measurement

app = Flask(__name__)
Bootstrap(app)

ENTITY_ID = 666
# 30 seconds between snapshot
SNAPSHOT_TIME_DELTA = 3000
SNAPSHOT_OFFSET_DELTA = 5000
GENERATOR_OPTION = True


def update_values(x, y):
    store_single_event(Event('jj', generate_timestamp(), x, y))


def store_single_event(event):
    store_events(ENTITY_ID, [event])


def get_times():
    past_events = find_events(ENTITY_ID)
    return [e.ts for e in past_events]


def split_data(entity):
    return_x = list()
    return_y = list()
    for x, y in sorted(entity.items()):
        return_x.append(x)
        return_y.append(y)

    return return_x, return_y


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


def time_strategy(events, entity):
    last_offset = events[-1].offset
    last_ts = events[-1].value.ts
    first_ts = events[0].value.ts

    if last_ts - first_ts > SNAPSHOT_TIME_DELTA:
        store_snapshot(entity_id=ENTITY_ID, entity=entity, offset=last_offset, ts=last_ts)


def distance_strategy(events, entity):
    last_offset = events[-1].offset
    last_ts = events[-1].value.ts

    if len(events) > SNAPSHOT_OFFSET_DELTA:
        store_snapshot(entity_id=ENTITY_ID, entity=entity, offset=last_offset, ts=last_ts)


def get_entity(ts):
    if ts == 0:
        ts = generate_timestamp()

    snapshotted = False
    entity, offset = select_snapshot(entity_id=ENTITY_ID, ts=ts)

    if entity:
        print('Got snapshot')
        snapshotted = True

    past_events = get_offsets(offset, ts)

    evs = len(past_events)
    entity = apply_events([e.value for e in past_events], entity=entity)

    # time_strategy(events=past_events, entity=entity)
    distance_strategy(past_events, entity)

    return entity, {'snapshotted': snapshotted, 'evs': evs}


@app.route('/times/', methods=['GET'])
def times():
    return jsonify({'times': get_times()})


@app.route('/pdata/', methods=['GET'])
@app.route('/pdata/<int:ts>', methods=['GET'])
def just_data(ts=0):
    entity, stats = get_entity(ts)

    return jsonify({
        'entity': entity,
        'stats': stats
    })


@app.route('/data/', methods=['GET'])
@app.route('/data/<int:ts>', methods=['GET'])
def get_data(ts=0):
    entity, _ = get_entity(ts)

    # just for fun, by each retrieval we add a new Event
    if ts == 0 and GENERATOR_OPTION:
        new_events = make_new_measurement(entity)
        entity = apply_events(new_events, entity)
        store_events(ENTITY_ID, new_events)

    # transformation for plotting
    x_vector, x_vector = split_data(entity)
    return jsonify(
        {
            'data': {
                'x': x_vector,
                'y': x_vector
            },
            'times': get_times(),
            'authors': get_authors()
        })


@app.route('/authors/', methods=['GET'])
@app.route('/authors/<author>', methods=['GET'])
def get_data_by_author(author=ORIGIN.author):
    past_events = find_events(ENTITY_ID)
    entity = apply_events([e for e in past_events if e.author == author])

    vector_x, vector_y = split_data(entity)
    return jsonify({
        "data": {
            'x': vector_x,
            'y': vector_y
            }
    })


@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


app.run(host='0.0.0.0', port=8080, debug=False)
