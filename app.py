import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
import flask_cors
from models import db, guard, User, Comment, Post, PostLike, Follow
from dotenv import load_dotenv
from seed import seed_data

load_dotenv()
app = Flask(__name__)
cors = flask_cors.CORS()
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
guard.init_app(app, User)
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)
cors.init_app(app)

with app.app_context():
    db.create_all()
    seed_data()

# blueprint for non-auth parts of app
from main import main as main_blueprint
app.register_blueprint(main_blueprint)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from users import userRoute as users_blueprint
app.register_blueprint(users_blueprint)

from posts import posts as posts_blueprint
app.register_blueprint(posts_blueprint)

# sample api endpoint
@app.route('/api/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # get parameters from post request
        parameters = request.get_json()
        if 'test' in parameters:
            return jsonify({'value': parameters['test']})
        return jsonify({'error'})
    else:
        return jsonify({'test': 'success'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)