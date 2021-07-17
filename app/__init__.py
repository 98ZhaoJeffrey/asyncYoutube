from .models import User, Room, db
from .utils import validateVideo

from flask import Flask, render_template, session, request, redirect
from os import getenv
from dotenv import load_dotenv, find_dotenv
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit
import redis, fakeredis


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

fakeRedisClient = fakeredis.FakeStrictRedis(decode_responses=True)
redisClient = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        data = request.form
        if 'make' in data:

            room = Room()
            username = data['name']
            link = data['video']
            user = User(name=username, room_code=room.code)
            room.host = user.id

            db.session.add(user)
            db.session.add(room)
            db.session.commit()

            link = validateVideo(link)
            if link:
                fakeRedisClient.lpush(room.code, link)
                session['user'] = {'username': user.name, 'room': room.code, 'id': user.id}
                return ({'success':'Room is sucessfully created. You will be redirected in a moment.'}, 201) 
            else:
                 ({'error':'This video does not exist'}, 404)

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
                
                return ({'success':'You will be redirected to the room. Please wait a moment.'}, 200)
            else:
                return ({'error': 'The room with the code you provided does not exist. Check if it is correct.'}, 404)
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
    print(data)
    video = validateVideo(data['link'])
    if video:
        fakeRedisClient.lpush(data['room'], video)
        emit('addVideoResponse', {'state':'success'}, broadcast=True, include_self=False, to=data['room'])
        print('Video successfully added to queue')
    #use client.lpush to append a link
    #use client.rpop(roomcode) to get the next link in queue

#pause/play video method
@socketio.on('playVideo')
def playVideo(data):
    print(data)
    emit('toggleVideo', {'state': data['state'], 'time':data['time']}, broadcast=True, include_self=False, to=data['room'])

#skip to x seconds of the video
@socketio.on('skipTo')
def skipTo(data):
    print(data)
    emit('jumpTo', {'time':data['time'], 'timeline':data['timelineValue']}, broadcast=True, include_self=False, to=data['room'])

#next video method to run the next video(used when finish or skipped)

@socketio.on('skipVideo')
def skipVideo(data):
    print(data)
    roomcode = data['room']
    room = Room.query.filter_by(code=roomcode).first()

    if room.host == data['userId']:
        nextVideo = fakeRedisClient.rpop(room.code)
        if nextVideo != None:
            print(f'Video Skipped. Now Playing {nextVideo}')
            emit('skipVideoResponse', {'state':'skipping', 'video': nextVideo}, broadcast=True, to=data['room'])
        else:
            emit('skipVideoResponse', {'state':'failed'}, broadcast=True, include_self=False, to=data['room'])
    else:
        print('You are not the host of the room')
        emit('skipVideoResponse', {'state':'failed'}, broadcast=True, include_self=False, to=data['room'])

@socketio.on('videoEnded')
def videoEnded(data):
    print('Getting next video')
    roomcode = data['room']
    room = Room.query.filter_by(code=roomcode).first()
    nextVideo = fakeRedisClient.rpop(room.code)
    if nextVideo:
        emit('playNextVideo', {'state': 'next', 'video': nextVideo}, broadcast=True, to=data['room'])
    else:
        emit('playNextVideo', {'state': 'no Video'}, broadcast=True, to=data['room'])