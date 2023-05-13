from errors import bad_request, forbidden, page_not_found, custom404
from models import Comment, Post, User, db, current_user
from flask import jsonify, request, Blueprint

posts = Blueprint('posts', __name__)

# get all posts
@posts.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify({
        'posts': [each_post.to_json() for each_post in posts]        
    })

# get a particular post
@posts.route('/api/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    if not post:
        return custom404("post not found")
    return jsonify(post.to_json())


# create post
@posts.route('/api/create-post', methods=['POST'])
def create_post():

    # author_id = current_user.id
    content_url = request.json.get('content_url', None) 
    body = request.json.get('body', None)

    new_post = Post(uploaded_content_url=content_url, body=body, author=current_user) # where author is the backref
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"msg": "Post Created."}), 201


# edit post
@posts.route('/api/edit-post/<int:id>', methods=['PUT'])
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
@posts.route('/delete-post/<int:id>', methods=['DELETE'])
def delete_post(id):

    post_to_delete = Post.query.get(id)

    if not post_to_delete:
        return custom404("post not found")
    
    elif post_to_delete.author_id != current_user.id:
        return forbidden("Operation not allowed!")
    
    else:
        db.session.delete(post_to_delete)
        db.session.commit()
        return jsonify({"msg": "Post Deleted."}), 204
        

# posts of the followed users
@posts.route('/api/followed_users_posts')
def followed_posts():
    following_users = current_user.following_to_list.all()
    followed_posts = []
    result = []

    for each_user in following_users:
        locate_user = User.query.get(each_user.following_to)
        followed_posts += locate_user.posts

    for each_post in followed_posts:
        result.append(each_post.to_json())
    
    return jsonify({"followed_posts": result})


# make comment
@posts.route('/api/posts/<int:id>/make_comment', methods=['POST'])
def make_comment(id):
    comm_body = request.json.get('body', None)
    post_to_comment_in = Post.query.get(id)
    post_author = User.query.get(post_to_comment_in.author_id)

    if not post_to_comment_in:
        return custom404("Post not found.")
    if comm_body == "" or comm_body is None:
        return bad_request("comment cannot be empty.")
    elif current_user.is_following(post_author) or current_user.id == post_author.id:        
        new_comm = Comment(body=comm_body, author_backref=current_user, post_backref=post_to_comment_in)
        db.session.add(new_comm)
        db.session.commit()    
        return jsonify({"msg": "comment added."})
    else:
        return forbidden("you need to follow the user in order make comments.")


# delete comment
@posts.route('/delete_comment/<int:id>', methods=['DELETE'])
def delete_comment(id):
    comm_to_delete = Comment.query.get(id)

    if not comm_to_delete:
        return custom404("comment not found")

    # needs to be the same author/user who made the comment else an admin or moderator
    elif current_user.id == comm_to_delete.author_id:      
        db.session.delete(comm_to_delete)
        db.session.commit()
        return jsonify({"msg": "Comment Deleted."}), 204
    else:
        return forbidden("Operation not allowed!")