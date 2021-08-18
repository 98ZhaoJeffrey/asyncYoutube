from app import *

if __name__ == '__main__':
    db.create_all()
    app.debug = bool(getenv('DEBUG', 1))
    app.env = getenv('ENV','development')
    app.testing = bool(getenv('TEST', 1))
    socketio.run(app, port=5000, host='0.0.0.0')