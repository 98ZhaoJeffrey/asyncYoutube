from .models import User, Room, db, to_dict
from .utils import validate_video, VideoQueue
from flask import Flask, render_template, session, request, redirect
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit

import redis
import fakeredis

from os import getenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.app = app
db.init_app(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)

videoQueue = VideoQueue(fakeredis.FakeStrictRedis(decode_responses=True))
#redisClient = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

from app import views
