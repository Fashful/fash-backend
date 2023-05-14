from urllib import response
from flask import request, jsonify

# custom 404 error
def custom404(message):
    # only accepting json request headers in response
    if request.accept_mimetypes.accept_json:
        response = jsonify({ "msg": message })
        return response

# 403 forbidden
def forbidden(message):
    response = jsonify({'error': 'forbidden', "msg": message})
    response.status_code = 403
    return response

# 400 bad request
def bad_request(message):
    response = jsonify({'error': 'bad request', "msg": message})
    response.status_code = 400
    return response

# 401 unauthorized
def unauthorized(message):
    response = jsonify({ 'error': 'unauthorized', "msg": message })
    response.status_code = 401
    return response