# Async Youtube

A website that lets users create and join rooms to watch Youtube videos together with the host with a chat and queue system.

## Features

Generate: Create a new room for others to join

Join: Join an existing room with other users

Chat: Discuss and comment on the video currently playing with other users

Queue: Add videos or playlists to the queue that automatically play or can be skipped by the host.

Host controls: Allow the host to play/pause/scrub the video and does the same to the other's screen

User controls: Adjust volume and size of the video

## Installation/Setup

Pull the repo to your computer

Docker

You will need to provide your own .env file containing the variables found inside the docker-compose file under environment

Run 
```bash
docker-compose up --build
```
and the website should be availiable on localhost:5000

Python

You need a redis and MySQL server and edit the 'SQLALCHEMY_DATABASE_URI' inside __init__.py for your local server

Create a new virtual enviroment by running
```python
python3 -m venv [yourVenvName]
[yourVenvName]\Scripts\activate.bat
```
Install the required packages 
```python
pip install -r requirements.txt
```
Set the Flask environment variable with
```bash
FLASK_APP=run.py
```
Run the website with 
```bash
flask run
```

