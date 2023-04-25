import uuid
from flask import Blueprint, request, jsonify
from models import db, guard, User
from utilities import success, failure
from sqlalchemy import func

auth = Blueprint('auth', __name__)

@auth.after_request  # blueprint can also be app~~
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

@auth.route('/api/auth/login', methods=['POST'])
def login_post():
    # get request info
    body = request.get_json()
    username = body['username']
    password = body['password']
    try:
        # authenticate user and send token
        user =  User.query.filter(func.lower(User.username) == func.lower(username)).first()
        if user:
            try:
                user = guard.authenticate(func.lower(username), password)
                if user:
                    if not user.is_active:
                        return failure({"error": "User is not active!"})
                    ret = {
                        'access_token': guard.encode_jwt_token(user, ),
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'name': user.name,
                        }
                    }
                    return success(data=ret)
                return failure("The username and password combination is incorrect.")
            except Exception as e:
                print(len(str(e)))
                if str(e) == "The username and/or password are incorrect (401)":
                    return failure({"error": "The username and password combination is incorrect."})
                return failure({"error": e})
        else:
            return failure({"error":"The username and password combination is incorrect."})
    except Exception as e:
        print("Something wrong")
        return failure({"error": e})

@auth.route('/api/auth/signup', methods=['POST'])
def signup_post():
    # get request info
    body = request.get_json()
    name = body['name']
    username = body['username']
    password = body['password']

    # if this returns a user, then the email already exists in database
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first()

    if user:  # if a user is found, redirect back to signup page so user can try again
        ret = {'error': 'User already exists'}
        return ret, 200

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    try:
        new_user = User(id=str(uuid.uuid4()), username=func.lower(username), name=name, 
                    hashed_password=guard.hash_password(password))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return success(data={"message": "User created successfully."})
    except Exception as e:
        print(e)

@auth.route('/api/auth/refresh', methods=['GET'])
def refresh():
    old_token = guard.read_token_from_header()
    new_token = guard.refresh_jwt_token(old_token)
    ret = {'access_token': new_token}
    return success(data=ret)