from collections import defaultdict

store = defaultdict(list)


def find_events(entity_id):
    return store[entity_id]


def store_events(entity_id, events):
    store[entity_id].extend(events)