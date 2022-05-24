from app import app, session, request, User, Room, db, to_dict

@app.route('/', methods=['GET'])
def hello():
    return ({'status':'Success', 'message': 'Hello World'}, 200)