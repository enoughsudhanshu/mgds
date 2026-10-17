from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from auth import auth
from donor import donor
from recipient import recipient
from admin import admin
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donation.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
app.register_blueprint(auth)
app.register_blueprint(donor)
app.register_blueprint(recipient)
app.register_blueprint(admin)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)