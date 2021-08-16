from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    room_code = db.Column(db.String(36), db.ForeignKey('room.code'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(uuid.uuid4())

    """ 
    def __str__(self):
        return str(self.username, self.room_code, self.id)
    """

class Room(db.Model):
    code = db.Column(db.String(36), primary_key=True)
    current_video = db.Column(db.String(64))
    
    #Get every user that is in the room for users, but only 1 person can be the host of the room
    users = db.relationship('User', backref='room')
    host = db.Column(db.String(64))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = str(uuid.uuid4())

    def __str__(self):
        return self.code

#__dict__ doesnt work for some reason
def to_dict(obj: object) -> dict:
    return {c.name:getattr(obj, c.name, None) for c in obj.__table__.columns}