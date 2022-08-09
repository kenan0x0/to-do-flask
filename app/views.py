import os, logging 
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

from app import app, lm, db, bc
from app.models import Users, Tasks

@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = None

    if request.method == "POST":

        username = request.form.get('register-username')
        password = request.form.get('register-password') 
        email = request.form.get('register-email')

        user = Users.query.filter_by(user=username).first()
        user_by_email = Users.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'

        else:         
            pw_hash = bc.generate_password_hash(password)
            user = Users(username, email, pw_hash)
            db.session.add(user)
            db.session.commit()
            msg = 'User created, you can now login.'

    return render_template('register.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = None

    if request.method == "POST":
        username = request.form.get('login-username')
        password = request.form.get('login-password')

        user = Users.query.filter_by(user=username).first()

        if user:
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template('login.html', msg=msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    if request.method == "POST":
        new_task = request.form.get("task")
        print(new_task)
    
    
    return render_template('index.html')

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    if request.method == "POST":
        new_task = request.form.get("task")
        label = request.form.get("label")
        task_date = request.form.get("task_date")
        print(new_task)
        print(label)
        print(task_date)
    
    
    return render_template('add-task.html')

@app.errorhandler(404)
def not_found(e):
  return redirect(url_for("index"))