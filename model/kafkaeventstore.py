from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
import json
import struct

from model import Event

TOPIC = 'measurements'
PARTITION_NUMBER = 1


def deserializer(key):
    try:
        return struct.unpack('>I', key)[0]
    except:
        return 0


def find_events(entity_id):
    # group_id = 'dashboards', client_id = 'me',
    consumer = KafkaConsumer(TOPIC, auto_offset_reset='earliest', bootstrap_servers='localhost:9092',
                             value_deserializer=lambda m: Event._make(json.loads(m.decode('ascii'))),
                             key_deserializer=deserializer, consumer_timeout_ms=100)
    # possibly not reverting to the beginning but rather use snapshots
    # consumer.seek(TopicPartition(topic=TOPIC, partition=PARTITION_NUMBER), 0)
    # for msg in consumer:
    #     print('%d --> %s' % (msg.key, msg.value))
    # return filter(lambda msg: msg.key == entity_id, consumer)
    return [msg.value for msg in consumer if msg.key == entity_id]


def store_events(entity_id, events):
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                             value_serializer=lambda m: json.dumps(m).encode('ascii'),
                             key_serializer=lambda k: struct.pack('>I', k))
    for e in events:
        producer.send(TOPIC, key=entity_id, value=e)
    producer.flush()
