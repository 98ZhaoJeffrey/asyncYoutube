from tests import unittest, VideoQueue, fakeredis, json

class TestVideoQueue(unittest.TestCase):

    def setUp(self):
        self.videoQueue = VideoQueue(fakeredis.FakeStrictRedis(decode_responses=True))
        self.key = 'testKey'
        self.host_sid = 'test_host_sid'

    def get_room(self):
        return self.videoQueue._get_obj(self.key)

    def add_data(self):
        self.videoQueue.queue_video(self.key, 'first')
        self.videoQueue.queue_video(self.key, 'second')
        self.videoQueue.queue_video(self.key, 'third')

    def test_queue_video_inital(self):
        self.videoQueue.queue_video(self.key, 'first')
        self.assertEqual(self.get_room(), {'current': 'first', 'queue': [], 'host_sid': ''}, 'Room filled with the current video and empty queue')

    def test_queue_video(self):
        self.add_data()
        self.assertEqual(self.get_room(), {'current': 'first', 'queue': ['second', 'third'], 'host_sid': ''}, 'Room filled with the current video and queue')

    def test_get_current_video(self):
        self.add_data()
        self.assertEqual(self.get_room()['current'], 'first' , 'Current video should be "first"')

    def test_get_next_video(self):
        self.add_data()
        self.assertEqual(self.videoQueue.get_next_video(self.key), 'second', 'Next video to queue should be "second"')

    def test_get_next_video_until_empty(self):
        self.add_data()
        #same as queueing next video until there is only 1 video left
        #pops the 'second' video
        self.videoQueue.get_next_video(self.key)
        self.assertEqual(self.videoQueue.get_next_video(self.key), 'third', 'Next video to queue should be "third"')
    
    def test_get_next_video_get_current_video(self):
        self.add_data()
        self.videoQueue.get_next_video(self.key)
        self.videoQueue.get_next_video(self.key)
        self.assertEqual(self.videoQueue.get_current_video(self.key), 'third')

    def test_set_host(self):
        self.get_room()
        self.assertEqual(self.videoQueue.set_host(self.key, self.host_sid), True)

    def test_get_host(self):
        self.get_room()
        self.videoQueue.set_host(self.key, self.host_sid)
        self.assertEqual(self.videoQueue.get_host(self.key), self.host_sid)
        
    def test_delete_room(self):
        self.videoQueue.delete_room(self.key)
        self.assertEqual(self.videoQueue.redis_client.get(self.key), None, 'Room should not exist')
    
    def tearDown(self):
        self.videoQueue.redis_client.flushall()