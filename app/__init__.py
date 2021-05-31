from .models import User, Room, db

from flask import Flask, render_template, session, request, redirect
from os import getenv
from dotenv import load_dotenv, find_dotenv
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit
import redis, requests 
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

queue = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        data = request.form
        if 'make' in data:
            #create a room first, then make the user the host
            room = Room()
            username = data['name']
            link = data['video']
            user = User(name=username, room_code=room.code)
            room.host = user.id

            db.session.add(user)
            db.session.add(room)
            db.session.commit()

            if len(link) > 43:
                #remove the list parameter
                link = link.split('&list')[0]
            request.get(link)
            #queue.lpush(room.code, 'test')
            session['user'] = {'username': user.name, 'room': room.code, 'id': user.id}
            return {'success':'Room is sucessfully created. You will be redirected in a moment.'}, 201
        
        #join a room
        elif 'join' in data:
            #return json for fetch
            roomcode = data['code']
            room = Room.query.filter_by(code=roomcode).first()
            if room:
                username = data['name']
                user = User(name=username, room_code=roomcode)

                db.session.add(user)
                db.session.commit()
                session['user'] = {'username': user.name, 'room': room.code, 'id': user.id}
                
                return {'success':'You will be redirected to the room. Please wait a moment.'}, 201
            else:
                return {'error': 'The room with the code you provided does not exist. Check if it is correct.'}, 404
    return render_template('index.html')


@app.route('/join/<roomcode>', methods=['GET', 'POST'])
def join(roomcode):
    if request.method == 'POST':
        data = request.form
        username = data['name']
        user = User(name=username, room_code=roomcode)

        db.session.add(user)
        db.session.commit()

        session['user'] = {'username': user.name, 'room': roomcode, 'id': user.id}
        return {'success':'You will be redirected to the room. Please wait a moment.'}, 201
    room = Room.query.filter_by(code=roomcode).first()
    if room:
        #page to pick username
        return render_template('join.html')
    #page to show error
    return render_template('error.html')

@app.route('/room')
def room():
    # pop the user, then pass it in a context
    user = session.pop('user', None)
    if user:
        context = {'user': user}
        #socketio.emit('my response', f'{user} has joined', broadcast=True)
        return render_template('room.html', context=context)
    return redirect('/')

@app.route('/roomtest')
def roomtest():
    return render_template('room.html')

@app.route('/about')
def about():
    return render_template('about.html')

@socketio.on('connectUser')
def connect(data):
    print(data)
    room = data['room']
    join_room(room)
    emit('joinChat', data['username'], broadcast=True, include_self=False, to=room)

@socketio.on('disconnectUser')
def disconnect(data):
    print(f'Client disconnected {data}')
    room = data['room']
    leave_room(room)
    emit('leaveChat', data['username'], broadcast=True, to=room)

@socketio.on('sendMessage')
def message(data):
    print(data)
    emit('message', data['message'], broadcast=True, include_self=False, to=data['room'])

@socketio.on('addVideo')
def queueVideo(data):
    print(data['link'])
    print(data['room'])

"""
@socketio.event
def join(data):
    username = data['username']
    room = data['room']
    print(f"{username} has joined room: {room}")
    join_room(room)
    send(username + ' has joined room.', room=room)
    #emit(username + ' has entered the room.', room=room)

@socketio.event
def leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    #emit(username + ' has left the room.', room=room)
"""
#next video method to run the next video(used run when finish or skipped)

#add video method to append a video to the list

#pause/play video method

