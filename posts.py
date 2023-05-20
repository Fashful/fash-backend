import random
import uuid
from errors import bad_request, forbidden, custom404
from models import Comment, Post, PostLike, User, db, current_user, auth_required
from flask import jsonify, request, Blueprint

posts = Blueprint('posts', __name__)

# 404 error for pages
@posts.app_errorhandler(404)
def page_not_found(e):
    # only accepting json request headers in response
    if request.accept_mimetypes.accept_json:
        response = jsonify({ "msg": 'Not Found'})
        return response, 404

# 500 error
@posts.app_errorhandler(500)
def page_not_found(e):
    # only accepting json request headers in response
    if request.accept_mimetypes.accept_json:
        response = jsonify({ "msg": 'Internal Server Error'})
        return response

# get all posts
@posts.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify({
        'posts': [each_post.to_json() for each_post in posts]        
    })

# get all posts by a user
@posts.route('/api/posts/<string:id>', methods=['GET'])
def get_posts_by_user(id):
    posts = Post.query.filter_by(author_id=id).all()
    return jsonify({
        'posts': [each_post.to_json() for each_post in posts]        
    })

# get a particular post
@posts.route('/api/posts/<string:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    if not post:
        return custom404("post not found")
    return jsonify(post.to_json())


# create post
@posts.route('/api/create-post', methods=['POST'])
@auth_required
def create_post():
    u = current_user()

    content_url = request.json.get('content_url', None) 
    body = request.json.get('body', None)
    # create unique id for post
    id = len(Post.query.all()) + 1
    id = str(id)

    new_post = Post(id=id, uploaded_content_url=content_url, body=body, author=u) # where author is the backref
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"msg": "Post Created."}), 201


# edit post
@posts.route('/api/edit-post/<string:id>', methods=['PUT'])
def edit_post(id):
    content_url = request.json.get('content_url', None)
    body = request.json.get('body', None)

    post_to_edit = Post.query.get_or_404(id)

    # if post do not exist
    if not post_to_edit:
        return page_not_found("Post Not Found")

    # forbidden the request, if post author id and logged user id are different
    elif post_to_edit.author_id != current_user.id:
        return forbidden("Operation not allowed!")
    
    else:
        post_to_edit.uploaded_content_url = post_to_edit.uploaded_content_url if content_url is None else content_url
        post_to_edit.body = post_to_edit.body if body is None else body
        db.session.add(post_to_edit)
        db.session.commit()

        return jsonify({"msg": "Post Updated."})


# delete post
@posts.route('/api/delete-post/<string:id>', methods=['DELETE'])
@auth_required
def delete_post(id):
    u = current_user()
    post_to_delete = Post.query.get(id)

    if not post_to_delete:
        return custom404("post not found")
    
    elif post_to_delete.author_id != u.id:
        return forbidden("Operation not allowed!")
    
    else:
        db.session.delete(post_to_delete)
        db.session.commit()
        return jsonify({"msg": "Post Deleted."}), 204
        

# posts of the followed users
@posts.route('/api/followed_users_posts')
@auth_required
def followed_posts():
    u = current_user()
    following_users = u.following_to_list.all()
    followed_posts = []
    result = []

    for each_user in following_users:
        locate_user = User.query.get(each_user.following_to)
        followed_posts += locate_user.posts

    for each_post in followed_posts:
        result.append(each_post.to_json())
    
    return jsonify({"followed_posts": result})

# posts of the followed users in random order
@posts.route('/api/followed_users_posts')
@auth_required
def followed_random_posts():
    u = current_user()
    following_users = u.following_to_list.all()
    followed_posts = []

    for each_user in following_users:
        locate_user = User.query.get(each_user.following_to)
        followed_posts += locate_user.posts

    random.shuffle(followed_posts)
    result = [each_post.to_json() for each_post in followed_posts]

    return jsonify({"followed_posts": result})


# make comment
@posts.route('/api/posts/<string:id>/make_comment', methods=['POST'])
@auth_required
def make_comment(id):
    comm_body = request.json.get('body', None)
    post_to_comment_in = Post.query.get(id)
    post_author = User.query.get(post_to_comment_in.author_id)
    u = current_user()

    if not post_to_comment_in:
        return custom404("Post not found.")
    if comm_body == "" or comm_body is None:
        return bad_request("comment cannot be empty.")
    elif u.is_following(post_author) or u.id == post_author.id:        
        new_comm = Comment(id=str(uuid.uuid4()), body=comm_body, author_backref=u, post_backref=post_to_comment_in)
        db.session.add(new_comm)
        db.session.commit()    
        return jsonify({"msg": "comment added."})
    else:
        return forbidden("you need to follow the user in order make comments.")
    
@posts.route('/api/like_unlike/<string:id>/', methods=['POST'])
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
@posts.route('/api/get_likes/<string:id>/', methods=['GET'])
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
