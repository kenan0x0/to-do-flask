from app import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user = user
        self.password = password
        self.email = email

class Tasks(db.Model, UserMixin):
    __tablename__ = 'Tasks'
    user_id = db.Column(db.Integer(), db.ForeignKey("Users.id"), primary_key=True, unique=False, nullable=False)
    task_body = db.Column(db.String(500))
    task_completed = db.Column(db.Boolean, default=False, unique=False, nullable=False)
    task_category = db.Column(db.String, unique=False, nullable=False)
    task_date = db.Column(db.Date, unique=False, nullable=True)