from time import time
import sys


from model.kafkaeventstore import initialize_store, get_producer, TOPIC, get_consumer, PARTITION_NUMBER
from model import generate_event, ORIGIN
from kafka import TopicPartition


def verify():
    partition = TopicPartition(topic=TOPIC, partition=0)
    c = get_consumer()
    c.assign([partition])
    c.seek(partition=partition, offset=0)

    print('Messages {} so far:'.format(c.topics()))
    for msg in c:
        print(msg)

    c.close()


def get_offsets(low, high_ts):
    consumer = get_consumer()
    partition = TopicPartition(topic=TOPIC, partition=PARTITION_NUMBER)
    consumer.assign([partition])
    consumer.seek(partition, low)

    ret = list()
    while True:
        ne = next(consumer)
        ret.append(ne)
        if ne.value.ts > high_ts:
            break

    return ret


if __name__ == "__main__":
    entity_id = 666
    initialize_store(entity_id=entity_id, origin=ORIGIN)

    batch_size = 1000
    if len(sys.argv) > 1:
        batch_size = int(sys.argv[1])

    event = ORIGIN

    for __ in range(0, 50):
        start = time()
        producer = get_producer()
        for _ in range(0, batch_size):

            event = generate_event(event)
            producer.send(TOPIC, key=entity_id, value=event, partition=PARTITION_NUMBER)

        producer.flush()
        producer.close()

        end = time()
        print('Uploaded {} took: {}'.format(batch_size, (end - start)))
