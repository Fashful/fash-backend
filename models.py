from datetime import datetime
from flask import abort
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian, current_user, auth_required

db = SQLAlchemy()
guard = Praetorian()

class Follow(db.Model):
    __tablename__ = 'follows'

    # id of a person who follows someone 
    follower_id = db.Column(
        db.String(100), db.ForeignKey('users.id'), primary_key=True)

    # id of the person to whom we are following to 
    following_to = db.Column(
        db.String(100), db.ForeignKey('users.id'), primary_key=True)

    # time when they got followed/started following
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@dataclass
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    hashed_password = db.Column(db.Text)
    roles = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_image_url = db.Column(db.Text)
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete')
    comments = db.relationship('Comment', backref='author_backref', lazy='dynamic')
    liked = db.relationship('PostLike', backref='user_like_backref', lazy='dynamic')

    # example if user1 follows user2 and user3 we have => [<Follow 1, 2>, <Follow 1, 3>]
    following_to_list = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower_backref', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # example if user3 follows user1 (current user) we have => [<Follow 3, 1>]
    got_followed_back_list = db.relationship(
        'Follow',
        foreign_keys=[Follow.following_to],
        backref=db.backref('following_to_backref', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'  
    )

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
    def get_email(self):
        return self.email
    
    @property
    def get_username(self):
        return self.username

    @classmethod
    def lookup(cls, email):
        """
        *Required Method*
        flask-praetorian requires that the user class implements a ``lookup()``
        class method that takes a single ``username`` argument and returns a user
        instance if there is one that matches or ``None`` if there is not.
        """
        return cls.query.filter_by(email=email).one_or_none()

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
            "email": self.email,
            "name": self.name,
            "roles": self.roles,
            "created_at": self.created_at,
            "user_image_url": self.user_image_url,
            "posts": self.posts,
            "comments": self.comments,
            "liked": self.liked,
            "following_to_list": self.following_to_list,
            "got_followed_back_list": self.got_followed_back_list
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def is_following(self, user):
        # print("user data ===>", user) # returns the whole user
        if user.id is None:
            return False

        # if result is empty (means None) then user is not following the given user
        # checking if current follower id gets a match with
        return self.following_to_list.filter_by(following_to=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow_data = Follow(follower_backref=self,
                                 following_to_backref=user)
            db.session.add(follow_data)
        else:
            abort(403, "you are already following the user")

    def unfollow(self, user):
        if self.is_following(user):
            user_to_unfollow = self.following_to_list.filter_by(
                following_to=user.id).first()
            if user_to_unfollow:
                db.session.delete(user_to_unfollow)
            else:
                abort(403, "user not found")
        else:
            abort(403, "you need to follow the user first.")

    def to_json(self):

        followers_data = []
        following_to_data = []

        user_followers = self.got_followed_back_list.all()
        user_followed = self.following_to_list.all()

        for each_follower in user_followers:
            locate_user = User.query.get(each_follower.follower_id)
            followers_data.append({
                "user_id": locate_user.id,
                "username": locate_user.username
            })

        for each_user in user_followed:
            locate_user = User.query.get(each_user.following_to)
            following_to_data.append({
                "user_id": locate_user.id,
                "username": locate_user.username
            })

        json_user = {
            'user_id': self.id,
            'username': self.username,
            'followers': followers_data,
            'following': following_to_data,
            'roles': self.roles,
            'profile_image': self.user_image_url,
            'email': self.email,
            'posts': [each_post.to_json() for each_post in self.posts]
        }

        return json_user

    def less_user_info_json(self):

        json_data = {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,
            'roles': self.roles,
            'profile_image': self.user_image_url, 
        }

        return json_data

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.String(100), primary_key=True)
    body = db.Column(db.Text)
    uploaded_content_url = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(100), db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post_backref', lazy='dynamic')
    likes = db.relationship('PostLike', backref='post_like_backref', lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % self.body
    
    def to_json(self):
        locate_user = User.query.get(self.author_id)     

        json_post = {
            'id': self.id,
            'author_details': locate_user.less_user_info_json(), 
            'uploaded_content_url': self.uploaded_content_url,
            'body': self.body,
            'timestamp': self.timestamp,
            'likes': [each_like.like_json() for each_like in self.likes],
            'comments': [each_comm.comment_in_json() for each_comm in self.comments.order_by(Comment.timestamp.desc())]
        }

        return json_post

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.String(100), primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(100), db.ForeignKey('users.id'))
    post_id = db.Column(db.String(100), db.ForeignKey('posts.id'))

    def comment_in_json(self):

        the_user = User.query.get(self.author_id)
        commented_by_user = the_user.less_user_info_json()

        json_response = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'commented_by': commented_by_user,
            'post_id': self.post_id
        }

        return json_response
    
class PostLike(db.Model):
    __tablename__ = 'postlikes'

    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'))
    post_id = db.Column(db.String(100), db.ForeignKey('posts.id'))

    def like_json(self):

        json_response = {
            'id': self.id,
            'liked_by': self.user_id,
            'post_liked': self.post_id,
            'liked_by_username': User.query.get(self.user_id).username,
            'liked_by_users': [each_user.less_user_info_json() for each_user in User.query.get(self.user_id).got_followed_back_list.all()]
        }

        return json_response
