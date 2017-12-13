import random
from time import sleep, time
import requests
from tqdm import tqdm


SNAPSHOT_TIME_DELTA = 3000
SNAPSHOT_OFFSET_DELTA = 5000


def get_times():
    g = requests.get('http://localhost:8080/times/')
    return g.json()['times']


def time_based_selection(times, last_ts):
    if last_ts == 0:
        last_ts = times[0]

    curr_idx = times.index(last_ts)

    for j in range(curr_idx, len(times)):
        if times[j] > last_ts + SNAPSHOT_TIME_DELTA * 1.2:
            return times[j]

    return -1


def random_selection(times, last_ts):
    return random.choice(times)


def offset_based_selection(times, last_ts):
    if last_ts == 0:
        last_ts = times[0]

    curr_idx = times.index(last_ts)
    idx = int(curr_idx + SNAPSHOT_OFFSET_DELTA * 1.2)
    if idx > len(times):
        return -1

    return times[idx]


def reverse_offset_based_selection(times, last_ts):
    if last_ts == 0:
        last_ts = times[-1]

    curr_idx = times.index(last_ts)
    idx = int(curr_idx - SNAPSHOT_OFFSET_DELTA * 1.2)
    if idx < 1:
        return -1

    return times[idx]


def format_time(td):
    return td.microseconds + 100000 * td.seconds


if __name__ == "__main__":
    times_list = get_times()
    res = list()
    ts = 0

    next_ts = reverse_offset_based_selection
   # next_ts = offset_based_selection
    # print('Using {} strategy'.format(next_ts.__name__))

    for i in tqdm(range(100)):
        ts = next_ts(times_list, ts)
        if ts == -1:
            break
        st = time()
        ent = requests.get('http://localhost:8080/pdata/{}'.format(ts))
        t1 = time() -st

        evs1 = ent.json()['stats']['evs']
        snap1 = ent.json()['stats']['snapshotted']
        sleep(.01)

        st = time()
        ent = requests.get('http://localhost:8080/pdata/{}'.format(ts))
        t2 = time() - st
        evs2 = ent.json()['stats']['evs']
        snap2 = ent.json()['stats']['snapshotted']

        res.append((t1, evs1, snap1, t2, evs2, snap2, len(ent.json()['entity'])))
        sleep(.01)

    print('time1,evns1,snap1,time2,evns2,snap2,rq')
    for line in res:
        print('{},{},{},{},{},{},{}'.format(line[0], line[1], line[2], line[3], line[4], line[5], line[6]))
