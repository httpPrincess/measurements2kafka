from kafka import KafkaConsumer, KafkaProducer


def get_address():
    import os
    server = os.getenv('KAFKA_PORT_9092_TCP_ADDR', 'localhost')
    port = os.getenv('KAFKA_PORT_9092_TCP_PORT', '9092')
    return server + ':' + port


def get_consumer():
    return KafkaConsumer(TOPIC, auto_offset_reset='earliest', bootstrap_servers=get_address())
     # value_deserializer=lambda m: Event._make(json.loads(m.decode('ascii'))),
     # key_deserializer=deserializer, consumer_timeout_ms=100)


def get_producer():
    return KafkaProducer(bootstrap_servers=get_address())
     # value_serializer=lambda m: json.dumps(m).encode('ascii'),
     # key_serializer=lambda k: struct.pack('>I', k))


CHUNK_SIZE = 1000
TOPIC = 'filetopic'


def get_chunk(fname, chunk_size=CHUNK_SIZE):
    with open(fname, 'r+b') as f:
        while True:
            chunk = f.read(chunk_size)
            if chunk:
                yield chunk
            else:
                break


producer = get_producer()
fname = 'binary.oo'
counter = 0
for chunk in get_chunk(fname):
    producer.send(TOPIC, key='%s.%d' % (fname, counter), value=chunk)

producer.flush()
