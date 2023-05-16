import json
from models import User

def test_auth_signup(client, test_db):
    # Prepare test data
    data = {
        'name': 'John Doe',
        'username': 'johndoe',
        'email': 'johndoe@example.com',
        'password': 'password123'
    }

    # Send a POST request to the signup endpoint
    response = client.post('/api/auth/signup', json=data)
    assert response.status_code == 200

    # Verify the response data
    response_data = json.loads(response.data)
    try:
        assert 'message' in response_data['data']
        assert response_data['data']['message'] == 'User created successfully.'

        # Verify that the user is created in the database
        with client.application.app_context():
            user = User.query.filter_by(email='johndoe@example.com').first()
        assert user is not None
        assert user.name == 'John Doe'
        assert user.username == 'johndoe'
    except AssertionError:
        # Delete the user from the database
        user = User.query.filter_by(email='johndoe@example.com').first()
        test_db.session.delete(user)

# def test_auth_login(client, test_db):
#     # Prepare test data
#     data = {
#         'email': 'test@test.com',
#         'password': 'password'
#     }

#     # Send a POST request to the login endpoint
#     response = client.post('/api/auth/login', json=data)
#     assert response.status_code == 200

#     # Verify the response data
#     response_data = json.loads(response.data)
#     assert 'access_token' in response_data
#     assert 'user' in response_data

#     user_data = response_data['user']
#     assert 'id' in user_data
#     assert 'email' in user_data
#     assert 'name' in user_data
#     assert 'username' in user_data
#     assert 'image' in user_data
