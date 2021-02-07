from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    room_code = db.Column(db.String(36), db.ForeignKey('room.code'))

    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)
        self.id = str(uuid.uuid4())

    def __str__(self):
        return self.name

class Room(db.Model):
    code = db.Column(db.String(36), primary_key=True)
    current_video = db.Column(db.String(64))
    
    #Get every user that is in the room for users, but only 1 person can be the host of the room
    users = db.relationship('User', backref='room')
    host = db.relationship('User', backref='room', uselist=False)


    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)
        self.code = str(uuid.uuid4())

    def __str__(self):
        return self.code

