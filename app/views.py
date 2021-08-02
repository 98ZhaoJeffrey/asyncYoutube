from app import app, render_template, session, request, redirect, User, Room, db, to_dict, validateVideo, fakeRedisClient, socketio, join_room, leave_room, emit
from random import choice

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        if 'make' in data:
            room = Room()
            username = data['name']
            link = data['video']
            user = User(username=username, room_code=room.code)
            room.host = user.id

            db.session.add(user)
            db.session.add(room)
            db.session.commit()

            link = validateVideo(link)
            if link != "None":
                fakeRedisClient.lpush(room.code, link)
                session['user'] = {'username': user.username, 'room': room.code, 'id': user.id}
                return ({'status':'Success', 'message': 'Room is sucessfully created. You will be redirected in a moment.'}, 201) 
            else:
                return ({'status':'Error', 'message': 'This video does not exist'}, 404)

        #join a room
        elif 'join' in data:
            #return json for fetch
            roomcode = data['code']
            room = Room.query.get(roomcode)
            if room:
                username = data['name']
                user = User(username=username, room_code=roomcode)

                db.session.add(user)
                db.session.commit()
                session['user'] = {'username': user.username, 'room': roomcode, 'id': user.id}
                
                return ({'status':'Success', 'message': 'You will be redirected to the room. Please wait a moment.'}, 200)
            else:
                return ({'status':'Error', 'message': 'The room with the code you provided does not exist. Check if it is correct.'}, 404)
    return render_template('index.html')

@app.route('/join/<roomcode>', methods=['GET', 'POST'])
def join(roomcode):
    if request.method == 'POST':
        data = request.form
        username = data['name']
        user = User(name=username, room_code=roomcode)

        db.session.add(user)
        db.session.commit()

        session['user'] = user
        #{'username': user.name, 'room': roomcode, 'id': user.id}
        return {'status':'Success', 'message': 'You will be redirected to the room. Please wait a moment.'}, 201
    room = Room.query.filter_by(code=roomcode).first()
    if room:
        #page to pick username
        return render_template('join.html')
    #page to show error
    return render_template('error.html')

@app.route('/room')
def room():
    # pop the user, then pass it in a context
    user = session.get('user', None)
    if user:
        context = {'user': user}
        joinUrl = f'{request.url_root}join/{user["room"]}'
        return render_template('room.html', context=context, joinUrl=joinUrl)
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@socketio.on('connect')
def connect():
    print('Client connected') 
    user = session.get('user', None)
    if user:
        print(user)   
        room = user['room']
        join_room(room)
        emit('joinChat', user['username'], broadcast=True, include_self=False, to=room)

@socketio.on('disconnect')
def disconnect():
    user = session.pop('user', None)
    if user:
        print(f'{user["username"]} disconnected')
        deletedUser = User.query.get(user["id"])
        room = Room.query.get(user["room"])
        db.session.delete(deletedUser)
        if room and len(room.users):        
            if user["id"] == room.host:
                newHost = choice(room.users)
                print(f"{newHost.username} is the new host of the room")
                room.host = newHost.id
                emit('leaveChat', {"userleft": user['username'], "newHost": newHost.username}, broadcast=True, to=user['room'])
            emit('leaveChat', {"userleft": user['username']}, broadcast=True, to=user['room'])
        else:
            print("Room deleted")
            db.session.delete(room)
            fakeRedisClient.delete(user['room'])
        db.session.commit()

@socketio.on('sendMessage')
def message(data):
    print(data)
    emit('message', data['message'], broadcast=True, include_self=False, to=data['room'])

@socketio.on('addVideo')
def queueVideo(data):
    print(data)
    video = validateVideo(data['link'])
    if video != "None":
        fakeRedisClient.lpush(data['room'], video)
        emit('addVideoResponse', {'state':'success'}, broadcast=True, include_self=False, to=data['room'])
        print('Video successfully added to queue')

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