from app import *

if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.env = 'development'
    app.testing = True
    socketio.run(app)