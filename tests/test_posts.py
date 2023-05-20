import pytest
from models import Post, User, Comment
import json

@pytest.fixture
def user_token(client, user):
    response = client.post('/api/auth/login', json={
        'email': 'test@test.com',
        'password': 'password'
    })
    return json.loads(response.data)['data']['access_token']

@pytest.fixture
def test_post(test_db, user):
    test_p = Post(
        id=101,
        uploaded_content_url='https://www.google.com',
        body='This is a test post',
        author_id=user
    )
    test_db.session.add(test_p)
    test_db.session.commit()
    yield

def test_get_all_posts(client, user_token):
    response = client.get('/api/posts', headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'posts' in response_data
    posts = response_data['posts']
    assert len(posts) == len(Post.query.all())

def test_create_posts(client, user_token):
    response = client.post('/api/create-post', json={
        'content_url': 'https://www.google.com',
        'body': 'This is a test post'
    }, headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'msg' in response_data
    assert response_data['msg'] == 'Post Created.'

def test_get_post_by_user(client, user):
    response = client.get(f'/api/posts/{user}')
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'posts' in response_data
    posts = response_data['posts']
    assert len(posts) == len(Post.query.filter_by(author_id=user).all())

def test_get_post_by_id(client):
    response = client.get(f'/api/posts/1')
    assert response.status_code == 200

def test_followed_posts(client, user_token):
    response = client.get(f'/api/followed_users_posts', headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

def test_followed_random_posts(client, user_token):
    response = client.get(f'/api/followed_users_posts', headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

def test_make_comment(client, user_token, test_post):
    response = client.post('/api/posts/101/make_comment', json={
        'post_id': 101,
        'body': 'This is a test comment'
    }, headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

def test_delete_post(client, user_token, test_post):
    response = client.delete(f'/api/delete-post/101', headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 204
