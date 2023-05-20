def test_api_test(client):
    response = client.get('/api/test')
    assert response.status_code == 200
    assert response.json == {'test': 'success'}
