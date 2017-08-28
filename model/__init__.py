from collections import namedtuple
from .eventstore import find_events, store_events
from time import time
from math import sqrt
from random import choice, random, uniform

Event = namedtuple('Event', ['author', 'ts', 'x', 'y'])


def next_step(y0, stepnbr, dt=0.5):
    return y0 + (0.5 - random()) * sqrt(dt) * uniform(0.0, stepnbr)


def generate_name():
    return choice(['jj', 'bob', 'marry'])


def generate_timestamp():
    return int(time() * 1000)


ORIGIN = Event('jj', generate_timestamp(), 0, 2.5)


def generate_event(previous_event=ORIGIN):
    x = previous_event.x + 1
    return Event(
        generate_name(),
        generate_timestamp(),
        x,
        next_step(previous_event.y, x)
    )


def avg(aggregate):
    y = 0.0
    if len(aggregate) == 0:
        return y

    for ev in aggregate:
        y += ev

    return y / len(aggregate)


def apply_events(past_events):
    result = dict()
    for ev in past_events:
        result[ev.x] = ev.y

    return result


def workflow():
    entity_id = 1
    past_events = find_events(entity_id)

    item = apply_events(past_events)
    a = avg(item)

    # newEvents = process_command(item, 'something')
    # store_events(newEvents)
