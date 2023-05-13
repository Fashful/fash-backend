from datetime import datetime
import os
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
import flask_praetorian

db = SQLAlchemy()
guard = flask_praetorian.Praetorian()

@dataclass
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    hashed_password = db.Column(db.Text)
    roles = db.Column(db.String(255))

    @property
    def identity(self):
        """
        *Required Attribute or Property*
        flask-praetorian requires that the user class has an ``identity`` instance
        attribute or property that provides the unique id of the user instance
        """
        return self.id

    @property
    def rolenames(self):
        """
        *Required Attribute or Property*
        flask-praetorian requires that the user class has a ``rolenames`` instance
        attribute or property that provides a list of strings that describe the roles
        attached to the user instance
        """
        try:
            return self.roles.split(",")
        except Exception:
            return []

    @property
    def password(self):
        """
        *Required Attribute or Property*
        flask-praetorian requires that the user class has a ``password`` instance
        attribute or property that provides the hashed password assigned to the user
        instance
        """
        return self.hashed_password

    @property
    def email(self):
        return self.username

    @classmethod
    def lookup(cls, username):
        """
        *Required Method*
        flask-praetorian requires that the user class implements a ``lookup()``
        class method that takes a single ``username`` argument and returns a user
        instance if there is one that matches or ``None`` if there is not.
        """
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        """
        *Required Method*
        flask-praetorian requires that the user class implements an ``identify()``
        class method that takes a single ``id`` argument and returns user instance if
        there is one that matches or ``None`` if there is not.
        """
        return cls.query.get(id)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "roles": self.roles,
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

@dataclass
class Follow(db.Model):
    __tablename__ = 'follows'

    # id of a person who follows someone 
    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # id of the person to whom we are following to 
    following_to = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # time when they got followed/started following
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@dataclass
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    sent_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    sent_for = db.Column(db.Integer, db.ForeignKey('users.id'))
    shared_message = db.Column(db.Boolean, default=False)
    shared_post_path = db.Column(db.String(200))
    shared_post_of_username = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message %r>' % self.body

    def msg_json(self):

        user_details = User.query.get(self.sent_for)        

        json_response = {
            'message_id': self.id,
            'sender': self.sent_by,
            'recipient_id': self.sent_for,
            'recipient_name': user_details.username,
            'sender_name': User.query.get(self.sent_by).username,
            'shared_status': self.shared_message,
            'shared_post_path': self.shared_post_path,
            'shared_post_of_username': self.shared_post_of_username,
            'body': self.body,
            'sent_on': self.timestamp
        }

        return json_response