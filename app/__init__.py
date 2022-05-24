from .models import User, Room, Topic, db, to_dict
from flask import Flask, session, request
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit

from os import getenv, urandom
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    getenv('MYSQL_USER'),
    getenv('MYSQL_PASSWORD'),
    getenv('MYSQL_HOST'),
    getenv('MYSQL_DATABASE')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.app = app
db.init_app(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)

#hashmap to convert users to their socketio requests id
user_to_sid = {}

from app import views
