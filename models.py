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