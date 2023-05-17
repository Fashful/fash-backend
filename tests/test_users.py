from models import User, guard
import pytest
import json
import uuid

@pytest.fixture
def user_token(client, user):
    response = client.post('/api/auth/login', json={
        'email': 'test@test.com',
        'password': 'password'
    })
    return json.loads(response.data)['data']['access_token']

def test_get_user(client, user):
    response = client.get(f'/api/users/{user}')
    assert response.status_code == 200

def test_update_username(client, user_token, user):
    response = client.post('/api/update_username', json={
        'new_username': 'test_user'
    }, headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert response.status_code == 200

def test_update_email(client, user_token, user):
    response = client.post('/api/update_email', json={
        'new_email': 'test_new@test.com',
    }, headers={
        'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200

def test_update_user_image(client, user_token, user):
    response = client.post('/api/update_image', json={
        'image_url': 'https://www.google.com'
    }, headers={
        'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200

# def test_update_password(client, user_token, user):
#     response = client.put('/api/update_password', json={
#         'new_password': 'new_password',
#         "old_password": "password"
#     }, headers={
#         'Authorization': f'Bearer {user_token}'})
#     assert response.status_code == 200

def test_get_user_profile(client, user):
    response = client.get(f'/api/user_profile/{user}')
    assert response.status_code == 200

def test_get_users_as_admin(client):
    response = client.get('/api/users')
    assert response.status_code == 200

def test_get_all_users(client):
    response = client.get('/api/all_users')
    assert response.status_code == 200

@pytest.fixture
def f_user(test_db):
    userid = str(uuid.uuid4())
    follow_user = User(id=userid, email="test1@test.com", name='Test Follow', username="testF",
                    hashed_password=guard.hash_password('password'))
    test_db.session.add(follow_user)
    test_db.session.commit()
    yield follow_user
    test_db.session.delete(follow_user)
    test_db.session.commit()

def test_follow_user(client, user_token, user, f_user):
    response = client.get(f'/api/follow/{f_user.username}', headers={
        'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200

def test_see_followers(client, user_token, user):
    response = client.get(f'/api/followers/test', headers={
        'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200

def test_unfollow_user(client, user_token, user, f_user):
    response = client.get(f'/api/follow/{f_user.username}', headers={
        'Authorization': f'Bearer {user_token}'})
    response = client.get(f'/api/unfollow/{f_user.username}', headers={
        'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200

def test_following_to(client, user_token, user):
    response = client.get(f'/api/following/test', headers={
        'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200

# def test_delete_user(client, user_token, user):
#     response = client.post(f'/api/user/{user}/delete', headers={
#         'Authorization': f'Bearer {user_token}'})
#     assert response.status_code == 200
