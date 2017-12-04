import json
import struct
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from model import Event

TOPIC = 'measurements'
PARTITION_NUMBER = 0
snapshots = dict()


def deserializer(key):
    try:
        return struct.unpack('>I', key)[0]
    except:
        return 0


def get_address():
    import os
    server = os.getenv('KAFKA_PORT_29092_TCP_ADDR', 'localhost')
    port = os.getenv('KAFKA_PORT_29092_TCP_PORT', '29092')
    return server + ':' + port


def get_consumer():
    return KafkaConsumer(bootstrap_servers=get_address(),
                         value_deserializer=lambda m: Event._make(json.loads(m.decode('ascii'))),
                         key_deserializer=deserializer, consumer_timeout_ms=100)


def get_producer():
    return KafkaProducer(bootstrap_servers=get_address(),
                         value_serializer=lambda m: json.dumps(m).encode('ascii'),
                         key_serializer=lambda k: struct.pack('>I', k))


def filter_entity_id(entity_id, events):
    return [msg.value for msg in events if msg.key == entity_id]


def find_events(entity_id):
    evs = find_with_offset()
    return filter_entity_id(entity_id=entity_id, events=evs)


def find_with_offset(offset_low=0, offset_high=-1):
    consumer = get_consumer()
    consumer.assign([TopicPartition(topic=TOPIC, partition=PARTITION_NUMBER)])
    consumer.seek(TopicPartition(topic=TOPIC, partition=PARTITION_NUMBER), offset_low)

    filter_function = None
    if offset_high != -1:
        filter_function = lambda msg: msg.offset <= offset_high

    return filter(filter_function, consumer)


def select_snapshot(entity_id, ts):
    tab = sorted([m for m in snapshots.keys() if (m[0] == entity_id and m[1] < ts)], key=lambda a: a[1])
    return snapshots[tab[-1]] if tab else ({}, 0)


def store_snapshot(entity_id, ts, entity, offset):
    snapshots[(entity_id, ts)] = (entity, offset)


def store_events(entity_id, events):
    producer = get_producer()
    for e in events:
        producer.send(TOPIC, key=entity_id, value=e)
    producer.flush()
    producer.close()


def initialize_store(entity_id, origin):
    store_events(entity_id, [origin])
