def test_api_main(client):
    response = client.get('/api/')
    assert response.status_code == 200
    assert response.text == "<h1>Hello World</h1>"
    assert response.headers['Access-Control-Allow-Origin'] == '*'
    assert response.headers['Access-Control-Allow-Headers'] == '*'
    assert response.headers['Access-Control-Allow-Methods'] == '*'
