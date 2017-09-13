from kafka import KafkaConsumer


def get_address():
    import os
    server = os.getenv('KAFKA_PORT_9092_TCP_ADDR', 'localhost')
    port = os.getenv('KAFKA_PORT_9092_TCP_PORT', '9092')
    return server + ':' + port


def get_consumer():
    return KafkaConsumer(TOPIC, auto_offset_reset='earliest', bootstrap_servers=get_address(), consumer_timeout_ms=100)
     # value_deserializer=lambda m: Event._make(json.loads(m.decode('ascii'))),
     # key_deserializer=deserializer, consumer_timeout_ms=100)


TOPIC = 'filetopic'

consumer = get_consumer()
counter = 0
current_fname = ''
f = None
for msg in consumer:
    fname, ext, chunk_nr = msg.key.split('.')
    fname = fname + ext
    if fname != current_fname:
        print('Got new file: %s' % fname)
        current_fname = fname
        if f:
            f.close()
        f = open('rcv'+current_fname, 'wb+')

    f.write(msg.value)

if f:
    f.close()
consumer.close()
