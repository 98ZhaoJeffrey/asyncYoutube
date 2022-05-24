from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    room_code = db.Column(db.String(36), db.ForeignKey('room.code'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(uuid4())

    def __str__(self):
        return self.username

class Room(db.Model):
    __tablename__ = 'room'
    code = db.Column(db.String(36), primary_key=True)

    # Multiple topics per room
    topics = db.relationship('Topic', backref='room')
    
    #Get every user that is in the room for users, but only 1 person can be the host of the room
    users = db.relationship('User', backref='room')
    host = db.Column(db.String(64))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = str(uuid4())

    def __str__(self):
        return self.code

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.String(36), primary_key=True)
    room_code = db.Column(db.String(36), db.ForeignKey('room.code'))
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    time_started = db.Column(db.DateTime, nullable=False)
    time_estimate = db.Column(db.Interval, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = str(uuid4())
        self.time_started = datetime.now().time()

    def __str__(self):
        return self.title


#__dict__ doesnt work for some reason
def to_dict(obj: object) -> dict:
    return {c.name:getattr(obj, c.name, None) for c in obj.__table__.columns}