import uuid
from flask import jsonify, request, Blueprint
from models import db, guard, User, Post, PostLike, current_user, auth_required
from errors import custom404, bad_request

likesRoute = Blueprint('likesRoute', __name__)

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