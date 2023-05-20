from datetime import datetime
from datetime import timezone
from datetime import timedelta
from errors import bad_request, custom404, forbidden
from models import Post, User, db, current_user, auth_required
from flask import jsonify, request, Blueprint
import cv2

userRoute = Blueprint('users', __name__)

# get user
@userRoute.route('/api/users/<string:id>')
def get_user(id):
    user = User.query.get(id)

    if not user:
        return custom404("User not found")
    return jsonify(user.to_json())


# update user name
@userRoute.route('/api/update_username', methods=['POST'])
@auth_required
def update_username():
    new_name = request.json.get('new_username')
    u = current_user()
    if new_name == "":
        return bad_request("username cannot be empty.")

    elif User.query.filter_by(username=new_name).first():
        return bad_request("username already taken.")

    get_user_id = u.id 
    
    u.username = new_name
    db.session.add(u)
    db.session.commit()

    return jsonify({"msg": "username updated."}), 200


# update user email
@userRoute.route('/api/update_email', methods=['POST'])
@auth_required
def update_email():
    new_email = request.json.get('new_email')
    u = current_user()
    if new_email == "":
        return bad_request("email cannot be empty.")

    elif User.query.filter_by(email=new_email).first():
        return bad_request("email already in use.")

    u.email = new_email
    db.session.add(u)
    db.session.commit()

    return jsonify({ "msg": "email updated."})


# update user image
@userRoute.route('/api/update_image', methods=['POST'])
@auth_required
def update_user_image():
    new_image_url = request.json.get('image_url')
    u = current_user()
    if not new_image_url:
        return bad_request("image field cannot be empty.")

    u.user_image_url = new_image_url
    db.session.add(u)
    db.session.commit()

    return jsonify({"msg": "profile picture updated."})


# update password
@userRoute.route('/api/update_password', methods=['PUT'])
@auth_required
def update_user_password():
    old_pass = request.json.get('old_password', None)
    new_pass = request.json.get('new_password', None)
    u = current_user()
    if old_pass == "":
        return bad_request("old password cannot be empty.")

    elif new_pass == "":
        return bad_request("new password cannot be empty")


    elif u.verify_password(old_pass):
        u.password = new_pass
        db.session.add(u)
        db.session.commit()
        return jsonify({"msg": "password updated"})
    else:
        return forbidden("incorrect old password.")


# get logged user profile
@userRoute.route('/api/user_profile/<string:id>')
def get_user_profile(id):    

    user = User.query.get(id)

    if not user:
        return custom404("User not found")
    return jsonify(user.to_json())

# Delete User
@userRoute.route('/api/user/<string:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)

    if not user:
        return custom404("User not found")
    else:
        old_pass = request.json.get('old_pass', None)

        if old_pass == "" or old_pass == None:
            return bad_request("password cannot be empty")

        if not user.verify_password(old_pass):
            return forbidden("incorrect password")

        deleted_by_admin = False
        # blocking the token of the user which is going to be removed
        # getting jti obj of currently logged in user token
        now = datetime.now(timezone.utc)
        db.session.commit()

    # deleting user
    db.session.delete(user)
    db.session.commit()

    custom_message = "User deleted (by admin)." if deleted_by_admin else "User deleted & token blocked."
    return jsonify({"msg": custom_message}), 204


# get all users with more info
@userRoute.route('/api/users')
def get_users_as_admin():
    users = User.query.all()
    return jsonify({"users": [each_user.to_json() for each_user in users]}), 200

# get all users
@userRoute.route('/api/all_users')
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [each_user.less_user_info_json() for each_user in users]}), 200


# follow a user
@userRoute.route('/api/follow/<username>')
@auth_required
def follow_user(username):
    user = User.query.filter_by(username=username).first()
    u = current_user()
    if not user:
        return custom404("user not found.")
    elif user.username == u.username:
        return bad_request("you cannot follow yourself.")    
    else:
        if u.is_following(user):
            return bad_request("already following the user.")
        else:
            u.follow(user)
            # not using db.session.add() here, as that is already defined in the follow method of User model
            db.session.commit()
            return jsonify({"msg": f"Started Following {username}."})


# unfollow a user
@userRoute.route('/api/unfollow/<username>')
@auth_required
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()
    u = current_user()
    if not user:
        return custom404("user not found.")
    else:
        if not u.is_following(user):
            return bad_request("you are not following this user already.")
        else:
            u.unfollow(user)
            # im not using db.session.add() here, as that is already defined in the follow method of User model
            db.session.commit()
            return jsonify({"msg": f"Unfollowed {username}."})

# user followers
@userRoute.route('/api/followers/<username>')
@auth_required
def see_followers(username):
    user = User.query.filter_by(username=username).first()
    u = current_user()
    if not user:
        return custom404("user not found")

    followers_data = []
    if user.username == u.username:
        my_followers = user.got_followed_back_list.all()
        for each_follower in my_followers:
            locate_user = User.query.get(each_follower.follower_id)
            followers_data.append(locate_user.username)
        return jsonify({"followers": followers_data})
    else:
        return forbidden("not allowed.")


# following to (returns current user following to list)
@userRoute.route('/api/following/<username>')
@auth_required
def see_following_to(username):
    user = User.query.filter_by(username=username).first()
    u = current_user()
    if not user:
        return custom404("user not found")

    following_to_data = []
    if user.username == u.username:
        user_followed = user.following_to_list.all()
        for each_user in user_followed:
            locate_user = User.query.get(each_user.following_to)
            following_to_data.append(locate_user.username)
        return jsonify({"following": following_to_data})
    else:
        return forbidden("not allowed.")
    
# search for users or posts with a keyword
@userRoute.route('/api/search/<string:keyword>')
def search(keyword):
    users = User.query.filter(User.username.contains(keyword)).all()
    posts = Post.query.filter(Post.body.contains(keyword)).all()
    return jsonify({"users": [user.to_json() for user in users], "posts": [post.to_json() for post in posts]})

# get similar posts for feed
@userRoute.route('/api/similar_posts', methods=['GET'])
@auth_required
def similar_color_posts():
    try:
        user = current_user()

        # Get the liked posts of the user
        liked_posts = [post_like.post_like_backref for post_like in user.liked]

        liked_hists = []
        for post in liked_posts:
            try:
                image = cv2.imread(post.uploaded_content_url)
                hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                liked_hists.append(hist)
            except:
                continue

        # Get the posts that are similar
        similar_posts = []
        for post in Post.query.all():
            try:
                image = cv2.imread(post.uploaded_content_url)
                hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()

                # Compare the histograms using the Bhattacharyya distance
                similarity = cv2.compareHist(liked_hists[0], hist, cv2.HISTCMP_BHATTACHARYYA)
                for i in range(1, len(liked_hists)):
                    similarity += cv2.compareHist(liked_hists[i], hist, cv2.HISTCMP_BHATTACHARYYA)
                similarity /= len(liked_hists)

                # Add the post to the list
                if similarity < 0.5:
                    similar_posts.append(post.to_json())
            except:
                continue

        # Return the list of similar posts
        return jsonify({'similar_posts': similar_posts})
    except Exception as e:
        return jsonify({'error': str(e)})
