from unittest import TestCase
from model import apply_events, Event, ORIGIN
from model import store_events, find_events


class Test_Logic(TestCase):

    def setUp(self):
        self.l1 = list()
        self.l1.append(ORIGIN)
        for k in range(1, 4):
            self.l1.append(Event('jj', 0, k, k*2))

    def tearDown(self):
        pass

    def test_inter(self):
        ENTITY_ID=666
        store_events(ENTITY_ID, self.l1)
        paste_events = find_events(ENTITY_ID)
        print paste_events
        self.assertEquals(len(paste_events), len(self.l1))

        res = apply_events(events=paste_events)
        self.assertEquals(len(res), len(self.l1))

    def test_sing(self):
        ENTITY_ID2 = 678
        store_events(ENTITY_ID2, [ORIGIN])
        past_events = find_events(ENTITY_ID2)

        res = apply_events(events=past_events)
        print res
        self.assertEquals(len(res), 1)
