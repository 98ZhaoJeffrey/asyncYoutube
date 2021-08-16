from app import app, render_template, session, request, redirect, User, Room, db, to_dict, validate_video, videoQueue, socketio, join_room, leave_room, emit, user_to_sid
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

            link = validate_video(link)
            if link:
                videoQueue.queue_video(room.code, link)
                session['user'] = {'username': user.username, 'room': room.code, 'id': user.id}
                return ({'status':'Success', 'message': 'Room is sucessfully created. You will be redirected in a moment.', 'video': link}, 201) 
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
        user = User(username=username, room_code=roomcode)
        db.session.add(user)
        db.session.commit()
        session['user'] = {'username': user.username, 'room': roomcode, 'id': user.id}
        return {'status':'Success', 'message': 'You will be redirected to the room. Please wait a moment.'}, 201
    room = Room.query.filter_by(code=roomcode).first()
    if room:
        #page to pick username
        return render_template('join.html')
    #page to show error
    return redirect('/')

@app.route('/room')
def room():
    # pop the user, then pass it in a context
    user = session.get('user', None)
    if user:
        join_url = f'{request.url_root}join/{user["room"]}'
        #peak the first video to load onto the iframe
        video = videoQueue.get_current_video(user['room'])
        print(video)
        data = {'user': user, 'join_url': join_url, 'video': video}
        return render_template('room.html', data=data)
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@socketio.on('connect')
def connect():
    user = session.get('user', None)
    if user:
        print(user, 'connected')  
        roomcode = user['room']
        join_room(roomcode)
        user_to_sid[user['id']] = request.sid
        room = Room.query.filter_by(code=roomcode).first() 
        data = user['username']        
        if room.host == user['id']:
            videoQueue.set_host(roomcode, request.sid)
        emit('joinChat', data, broadcast=True, include_self=False, to=room)

@socketio.on('disconnect')
def disconnect():
    user = session.pop('user', None)
    if user:
        roomcode = user['room']
        print(f'{user["username"]} disconnected')
        deleted_user = User.query.get(user['id'])
        room = Room.query.get(roomcode)

        db.session.delete(deleted_user)
        user_to_sid.pop(user['id'])

        if room and len(room.users):        
            if user['id'] == room.host:
                new_host = choice(room.users)
                print(f'{new_host.username} is the new host of the room')

                room.host = new_host.id
                videoQueue.set_host(roomcode, user_to_sid[new_host.id])

                data = {'userleft': user['username'], 'newHost': new_host.username}
                emit('leaveChat', data, broadcast=True, to=roomcode)
            data = {'userleft': user['username']}
            emit('leaveChat', data, broadcast=True, to=roomcode)
        else:
            print('Room deleted')
            db.session.delete(room)
            videoQueue.delete_room(user['room'])
        db.session.commit()

@socketio.on('syncVideo')
def syncVideo(data):

    roomcode = data['roomcode']
    host = videoQueue.get_host(roomcode)
    data = data['userId']
    emit('getVideoProgress', data, to=host)

@socketio.on('sendMessage')
def message(data):
    print(data)
    emit('message', data['message'], broadcast=True, include_self=False, to=data['room'])

@socketio.on('addVideo')
def queueVideo(data):
    print(data)
    room = data['room']
    video = validate_video(data['link'])
    if video:
        videoQueue.queue_video(room, video)
        data = {'status':'Success', 'message': 'Video successfully added to queue'}
        emit('addVideoResponse', data, include_self=True, to=request.sid)
        print('Video successfully added to queue')
    else:
        data = {'status':'Error', 'message': 'Video could not be added to queue'}
        emit('addVideoResponse', data, include_self=True, to=request.sid)
        print('Failed to push to queue')

#pause/play video method
@socketio.on('playVideo')
def playVideo(data):
    print(data)
    code = data['room']
    room = Room.query.filter_by(code=code).first()
    if room.host == data['userId']:
        data = {'state': data['state'], 'time':data['time']}
        emit('toggleVideo', data, broadcast=True, include_self=True, to=code)

#skip to x seconds of the video
@socketio.on('skipTo')
def skipTo(data):
    print(data)
    code = data.get('room', None)
    if code:
        room = Room.query.filter_by(code=code).first()
        if room.host == data['userId']:
            data = {'time':data['time'], 'timeline':data['timelineValue']}
            emit('jumpTo', data, broadcast=True, include_self=False, to=code)
    else:
        sid = user_to_sid[data['userId']]
        data = {'time':data['time'], 'timeline':data['timelineValue']}
        print(data)
        emit('jumpTo', data, to=sid)

#next video method to run the next video(used when finish or skipped)
@socketio.on('skipVideo')
def skipVideo(data):
    print(data)
    code = data['room']
    room = Room.query.filter_by(code=code).first()
    if room.host == data['userId']:
        next_video = videoQueue.get_next_video(room.code)
        if next_video:
            print(f'Video Skipped. Now Playing {next_video}')
            data = {'status':'Success', 'video': next_video, 'message': 'Video successfully skipped'}
            emit('skipVideoResponse', data, broadcast=True, include_self=True, to=code)
        else:
            data = {'status':'Error', 'message': 'There is no video to queue next'}
            emit('skipVideoResponse', data, include_self=True, to=request.sid)
    else:
        print('You are not the host of the room')
        data = {'status':'Error', 'message': "You are not the room's host"}
        emit('skipVideoResponse', data, include_self=True, to=request.sid)

@socketio.on('videoEnded')
def videoEnded(data):
    print('Getting next video')
    code = data['room']
    room = Room.query.filter_by(code=code).first()
    next_video = videoQueue.get_next_video(code)
    if next_video:
        data = {'status': 'Success', 'video': next_video, 'message': 'playing next video'}
        emit('playNextVideo', data, broadcast=True, to=code)
    else:
        data = {'status': 'Error', 'message':'The queue is empty'}
        emit('playNextVideo', data, broadcast=True, to=code)