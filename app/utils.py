import requests, json

def validate_video(link: str) -> str:
    '''
    Returns the video id if the video exists, otherwise returns none string
    '''
    if len(link) > 43:
        #remove the list parameter
        link = link.split('&list')[0]
    #get the video id
    try:
        id = link.split("=")[1]
    except IndexError:
        return ''
    server_response = requests.get(f'http://img.youtube.com/vi/{id}/mqdefault.jpg')
    try:
        #throws error if response is not OK
        server_response.raise_for_status()
        #print(f'video found: {id}')
        return id
    except requests.exceptions.HTTPError:
        #print('video not found')
        return ''

class VideoQueue():
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def _get_obj(self, key: str) -> dict:
        '''
        Return dictionary with key for current video and the queue
        '''
        try:
            return json.loads(self.redis_client.get(key))
        except TypeError:
            return {'current': '', 'queue': []}
    
    def _set_obj(self, key: str, obj: object) -> bool:
        '''
        Sets the key with a dictionary
        '''
        return self.redis_client.set(key, json.dumps(obj))

    def _set_current_video(self, key: str, video: str) -> bool:
        '''
        Sets the current video of the room
        '''
        room_obj = self._get_obj(key)
        room_obj['current'] = video
        return self._set_obj(key, room_obj)


    def get_current_video(self, key: str) -> str:
        '''
        Returns the current video that the room is playing
        '''
        return self._get_obj(key)['current']

    def get_next_video(self, key: str) -> str:
        '''
        Pops the video in the queue and set it as the current video
        '''
        room_obj = self._get_obj(key)
        try:
            next_video = room_obj['queue'].pop(0)
            room_obj['current'] = next_video
            self._set_obj(key, room_obj)
            return next_video
        except IndexError:
            return ''

    def queue_video(self, key: str, video: str) -> bool:
        room_obj = self._get_obj(key)
        #if it is the first video of the queue, dont add to queue since getting the next video will return the same video as the current video
        if room_obj['current']:
            room_obj['queue'].append(video)
        else:
            room_obj['current'] = video
        return self._set_obj(key, room_obj)
    
    def delete_room(self, key: str) -> bool:
        return self.redis_client.delete(key)