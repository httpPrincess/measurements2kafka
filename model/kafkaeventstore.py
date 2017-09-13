import json
import struct
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from model import Event

TOPIC = 'measurements'
PARTITION_NUMBER = 1


def deserializer(key):
    try:
        return struct.unpack('>I', key)[0]
    except:
        return 0


def get_address():
    import os
    server = os.getenv('KAFKA_PORT_9092_TCP_ADDR', 'localhost')
    port = os.getenv('KAFKA_PORT_9092_TCP_PORT', '9092')
    return server + ':' + port


def get_consumer():
    return KafkaConsumer(TOPIC, auto_offset_reset='earliest', bootstrap_servers=get_address(),
                         value_deserializer=lambda m: Event._make(json.loads(m.decode('ascii'))),
                         key_deserializer=deserializer, consumer_timeout_ms=100)


def get_producer():
    return KafkaProducer(bootstrap_servers=get_address(),
                         value_serializer=lambda m: json.dumps(m).encode('ascii'),
                         key_serializer=lambda k: struct.pack('>I', k))


def find_events(entity_id):
    # group_id = 'dashboards', client_id = 'me',
    consumer = get_consumer()
    # possibly not reverting to the beginning but rather use snapshots
    # consumer.seek(TopicPartition(topic=TOPIC, partition=PARTITION_NUMBER), 0)
    # for msg in consumer:
    #     print('%d --> %s' % (msg.key, msg.value))
    # return filter(lambda msg: msg.key == entity_id, consumer)
    return [msg.value for msg in consumer if msg.key == entity_id]


def store_events(entity_id, events):
    producer = get_producer()
    for e in events:
        producer.send(TOPIC, key=entity_id, value=e)
    producer.flush()


def initialize_store(entity_id, origin):
    store_events(entity_id, [origin])
