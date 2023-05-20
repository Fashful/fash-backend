import pytest
import json
from models import Post

@pytest.fixture
def user_token(client, user):
    response = client.post('/api/auth/login', json={
        'email': 'test@test.com',
        'password': 'password'
    })
    return json.loads(response.data)['data']['access_token']

@pytest.fixture
def test_post(test_db, user):
    post = Post(
        id='101',
        uploaded_content_url='https://www.google.com',
        body='This is a test post',
        author_id=user
    )
    test_db.session.add(post)
    test_db.session.commit()
    yield post
    if Post.query.get(post.id):
        test_db.session.delete(post)
        test_db.session.commit()

def test_like(client, user_token, test_post):
    response = client.post(f'/api/like_unlike/{test_post.id}/', headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json['msg'] == 'Post Liked'

    response = client.post(f'/api/like_unlike/{test_post.id}/', headers={
        "Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json['msg'] == 'Post Unliked'
