from app import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))
    user_image = db.Column(db.String(), unique=False, nullable=True)
    creation_time = db.Column(db.Date, nullable=False, unique=False)
    gender = db.Column(db.String(), unique=False, nullable=True, default=None)
    full_name = db.Column(db.String(), unique=False, nullable=True, default=None)
    city = db.Column(db.String(), unique=False, nullable=True, default=None)

    def __init__(self, user, email, password, user_image, creation_time):
        self.user = user
        self.email = email
        self.password = password
        self.user_image = user_image
        self.creation_time = creation_time
        


class Tasks(db.Model, UserMixin):
    __tablename__ = 'Tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("Users.id"), unique=False, nullable=False)
    task_title = db.Column(db.String(100))
    task_body = db.Column(db.String(500))
    task_completed = db.Column(db.Boolean, default=False, unique=False, nullable=False)
    task_category = db.Column(db.String, unique=False, nullable=False)
    task_date = db.Column(db.Date, unique=False, nullable=True)