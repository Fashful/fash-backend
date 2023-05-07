from dotenv import load_dotenv
from flask import Blueprint

main = Blueprint('main', __name__)

load_dotenv()

@main.after_request 
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

@main.route('/api/')
def hello():
    return "<h1>Hello World</h1>"