from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin_email = "enough@gmail.com"
    existing = User.query.filter_by(email=admin_email).first()
    
    if existing:
        print("Admin already exists!")
    else:
        admin = User(
            name="System Admin",
            email=admin_email,
            password_hash=generate_password_hash("enough123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created! Email: enough@gmail.com | Password: enough123")