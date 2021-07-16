import requests, time


def validateVideo(link):
    if len(link) > 43:
        #remove the list parameter
        link = link.split('&list')[0]

    #get the video id
    try:
        id = link.split("=")[1]
    except IndexError:
        return False
    
    serverResponse = requests.get(f"http://img.youtube.com/vi/{id}/mqdefault.jpg")

    try:
        #throws error if response is not OK
        serverResponse.raise_for_status()
        print("video found")
        return True

    except requests.exceptions.HTTPError:
        print("video not found")
        return False
