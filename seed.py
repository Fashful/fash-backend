from app import db
from models import User, Post, Comment, PostLike, Follow
import csv

# convert the csv file from data_csvs to dictionary
def csv_to_dict(filename):
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        return list(csv_reader)
    
users = csv_to_dict('data_csvs/users.csv')
posts = csv_to_dict('data_csvs/posts.csv')
comments = csv_to_dict('data_csvs/comments.csv')
post_likes = csv_to_dict('data_csvs/post_likes.csv')
follows = csv_to_dict('data_csvs/follows.csv')

def seed_data():
    # Delete all existing data from the tables
    db.session.query(User).delete()
    db.session.query(Post).delete()
    db.session.query(Comment).delete()
    db.session.query(PostLike).delete()
    db.session.query(Follow).delete()

    # Insert new data into the tables
    for user in users:
        db.session.add(User(**user))

    for post in posts:
        db.session.add(Post(**post))

    for comment in comments:
        db.session.add(Comment(**comment))

    for post_like in post_likes:
        db.session.add(PostLike(**post_like))

    for follow in follows:
        db.session.add(Follow(**follow))

    db.session.commit()