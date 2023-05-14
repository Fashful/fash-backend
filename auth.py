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
    email = body['email']
    password = body['password']
    try:
        # authenticate user and send token
        user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
        if user:
            try:
                user = guard.authenticate(func.lower(email), password)
                if user:
                    ret = {
                        'access_token': guard.encode_jwt_token(user, ),
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'name': user.name,
                            'username': user.username,
                        }
                    }
                    return success(data=ret)
                return failure("The uemail and password combination is incorrect.")
            except Exception as e:
                print(len(str(e)))
                if str(e) == "The email and/or password are incorrect (401)":
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
    email = body['email']
    password = body['password']

    # if this returns a user, then the email already exists in database
    user = User.query.filter(User.username==username).first()
    em = User.query.filter(func.lower(User.email) == func.lower(email)).first()

    if user: 
        ret = {'error': 'Username already exists'}
        return ret, 200
    
    if em: 
        ret = {'error': 'Email already exists'}
        return ret, 200

    try:
        new_user = User(id=str(uuid.uuid4()), email=func.lower(email), name=name, username=username,
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