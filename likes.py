import uuid
from flask import jsonify, request, Blueprint
from models import db, guard, User, Post, PostLike, current_user, auth_required
from errors import custom404, bad_request

likesRoute = Blueprint('likesRoute', __name__)

@likesRoute.after_request  # blueprint can also be app~~
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

@likesRoute.route('/api/like_unlike/<string:id>/', methods=['POST'])
@auth_required
def like_or_unlike(id): # id of post to like or unlike
    u = current_user()
    located_post = Post.query.get(id)
    if not located_post:
        return custom404("Post not found.")

    find_like = PostLike.query.filter_by(user_id=u.id, post_id=id).first()

    # if liked already then we will remove the liked entry (means unlike)
    if find_like:
        db.session.delete(find_like)
        db.session.commit()
        return jsonify({ "msg": "Post Unliked", "post_id": id, "updated_post": Post.query.get(id).to_json() }), 200

    new_like = PostLike(id=str(uuid.uuid4()) ,user_like_backref=u, post_like_backref=located_post)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({ "msg": "Post Liked", "post_id": id, "updated_post": Post.query.get(id).to_json() }), 200

# Get all likes for a post in a list of user ids
@likesRoute.route('/api/get_likes/<string:id>/', methods=['GET'])
@auth_required
def get_likes(id):
    located_post = Post.query.get(id)
    if not located_post:
        return custom404("Post not found.")

    likes = PostLike.query.filter_by(post_id=id).all()
    if not likes:
        return jsonify({ "msg": "No likes found for this post." }), 200

    likes_list = []
    for like in likes:
        likes_list.append(like.user_id)

    return jsonify({ "msg": "Likes found.", "likes": likes_list }), 200