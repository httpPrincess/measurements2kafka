from unittest import TestCase
from model import eventstore


class Test_events(TestCase):
    def setUp(self):
        print 'Setting up'
        eventstore.store.clear()
        super(Test_events, self).setUp()

    # def tearDown(self):


    def test_find_events(self):
        entity_id = 1
        res1 = eventstore.find_events(entity_id=entity_id)
        self.assertIsInstance(res1, list)
        self.assertEqual(len(res1), 0)

    def test_store_noevents(self):
        entity_id = 2
        eventstore.store_events(entity_id, [])
        self.assertEquals(len(eventstore.find_events(entity_id)), 0)

    def test_single_event(self):
        entity_id = 2
        eventstore.store_events(entity_id=entity_id, events='2')

        self.assertEquals(len(eventstore.find_events(entity_id)), 1)
        self.assertTrue('2' in eventstore.find_events(entity_id))

    def test_list_of_events(self):
        entity_id = 2
        eventstore.store_events(entity_id=entity_id, events=['5', '6'])

        self.assertEquals(len(eventstore.find_events(entity_id)), 2)
        self.assertTrue('5' in eventstore.find_events(entity_id))
        self.assertTrue('6' in eventstore.find_events(entity_id))
        self.assertTrue('2' not in eventstore.find_events(entity_id))

    def test_subsequent_additions(self):
        entity_id = 7
        l1 = ['99', '100']
        eventstore.store_events(entity_id=entity_id, events=l1)
        self.assertEquals(len(eventstore.find_events(entity_id)), len(l1))
        for l in l1:
            self.assertTrue(l in eventstore.find_events(entity_id))

        l2 = ['200', '300']
        eventstore.store_events(entity_id=entity_id, events=l2)
        self.assertEquals(len(eventstore.find_events(entity_id)), len(l1) + len(l2))
        for l in l1:
            self.assertTrue(l in eventstore.find_events(entity_id))
        for l in l2:
            self.assertTrue(l in eventstore.find_events(entity_id))
