from unittest import TestCase
from model import apply_events, Event, avg


class Test_Model(TestCase):

    def setUp(self):
        self.l1 = list()
        for k in range(0, 3):
            self.l1.append(Event('jj', 0, k, k*2))

    def tearDown(self):
        pass

    def test_apply_noevents(self):
        res = apply_events([])
        self.assertEquals(len(res),0, 'There should be no events')

    def test_apply_simple_events(self):
        res = apply_events(self.l1)
        self.assertEquals(len(res), 3)

    def test_apply_same_events(self):
        res1 = apply_events(self.l1)
        res2 = apply_events(self.l1 + self.l1)
        self.assertEquals(res1, res2, 'There should be no difference')

    def test_apply_correction(self):
        res1 = apply_events(self.l1+[Event('jj', 0, 1, 19)])
        self.assertEquals(len(res1), len(self.l1))
        self.assertEquals(res1[1], 19)

    def test_map_red(self):
        res = apply_events(self.l1)
        sum = reduce(lambda x,y: x+y, res)
        avg1 = sum/len(res)
        res1 = avg(res)
        self.assertEquals(res1, avg1)
