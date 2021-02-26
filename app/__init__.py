from .models import User, Room, db

from flask import Flask, render_template, session, request, redirect
from os import getenv
from dotenv import load_dotenv, find_dotenv
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit


load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)


@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        #can just use axios and js to redirect/handle json
        data = request.form
        if 'make' in data:
            #create a room first, then make the user the host
            room = Room()
            username = data['name']
            user = User(name=username, room_code=room.code)
            room.host = user.id

            db.session.add(user)
            db.session.add(room)
            db.session.commit()
            return {'success':'Room is sucessfully created. You will be redirected in a moment.'}, 200
        
        #join a room
        elif 'join' in data:
            #return ajax method
            roomcode = data['code']
            room = Room.query.filter_by(code=roomcode).first()
            if room:
                return {'success':'You will be redirected to the room. Please wait a moment.'}, 200
            else:
                return {'error': 'The room with the code you provided does not exist. Check if it is correct.'}, 404
    return render_template('index.html')

"""
@app.route('/join/<roomcode>', methods=['GET', 'POST'])
def join(roomcode):
    if request.method == 'POST':
        room = Room.query.filter_by(code=request.form['roomcode'])
        if room:
            #redirect
            pass
    room = Room.query.filter_by(code=roomcode)
    if room:
        #page to pick username
        pass
    #page to show error and give a form to try again
    pass
"""

@app.route('/room')
def room():
    return render_template('room.html')

@app.route('/about')
def about():
    return render_template('about.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    #emit(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    #emit(username + ' has left the room.', room=room)

