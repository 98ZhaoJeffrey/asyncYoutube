from tests import unittest, validate_video

class TestValidateVideo(unittest.TestCase):

    def setUp(self):
        self.tests = {
            'public_video': {
                'link': 'https://www.youtube.com/watch?v=zMFb8Y2QLPc', 
                'result': 'zMFb8Y2QLPc'
            },
            'unlisted_video': {
                'link': 'https://www.youtube.com/watch?v=YQe3weqf_To',
                'result': 'YQe3weqf_To'
            },
            'private_video': {
                'link': 'https://www.youtube.com/watch?v=6Xj6VMKM9W4',
                'result': ''
            },
            'playlist_video': {
                'link': 'https://www.youtube.com/watch?v=mQndlrEHbOU&list=RDmQndlrEHbOU&start_radio=1', 
                'result': 'mQndlrEHbOU'
            },
            'fake_video': {
                'link':'https://www.youtube.com/watch?v=mQndlrEHbOa', 
                'result': ''
            },
            'live_stream': {
                'link': 'https://www.youtube.com/watch?v=5qap5aO4i9A',
                'result': '5qap5aO4i9A'
            }
        }

    def test_public_video(self):
        self.assertEqual(validate_video(self.tests['public_video']['link']), self.tests['public_video']['result'], 'Should succeed and return video ID')

    def test_private_video(self):
        self.assertEqual(validate_video(self.tests['private_video']['link']), self.tests['private_video']['result'], 'Should fail and return empty string')

    def test_unlisted_video(self):
        self.assertEqual(validate_video(self.tests['unlisted_video']['link']), self.tests['unlisted_video']['result'], 'Should succeed and return video ID')

    def test_playlist_video(self):
        self.assertEqual(validate_video(self.tests['playlist_video']['link']), self.tests['playlist_video']['result'], 'Should succeed and return video ID')

    def test_fake_video(self):
        self.assertEqual(validate_video(self.tests['fake_video']['link']), self.tests['fake_video']['result'], 'Should fail and return empty string')
    
    def test_live_stream(self):
        self.assertEqual(validate_video(self.tests['live_stream']['link']), self.tests['live_stream']['result'], 'Should succeed and return video ID')