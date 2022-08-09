import os, logging 
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

from app import app, lm, db, bc
from app.models import Users, Tasks

from datetime import datetime

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
    cate = None

    if request.method == "POST":

        username = request.form.get('register-username')
        password = request.form.get('register-password') 
        email = request.form.get('register-email')

        user = Users.query.filter_by(user=username).first()
        user_by_email = Users.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
            cate = 'error'

        else:         
            pw_hash = bc.generate_password_hash(password)
            user = Users(username, email, pw_hash)
            db.session.add(user)
            db.session.commit()
            msg = 'User created, you can now login.'
            cate = 'success'

    return render_template('register.html', msg=msg, cate=cate)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = None
    cate = None

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
                cate = 'error'
        else:
            msg = "Unknown user"
            cate = 'error'

    return render_template('login.html', msg=msg, cate=cate)

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    user_name = Users.query.filter_by(email=current_user.email).first().user
    if request.method == "POST":
        print("hello")
    
    
    return render_template('index.html', user_name=user_name)

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    msg = None
    cate = None

    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_name = Users.query.filter_by(email=current_user.email).first().user
    user_task_categories = [task.task_category for task in Tasks.query.filter_by(user_id=user_id).all()]

    if request.method == "POST":
        task_title = request.form.get("task-title")
        new_task = request.form.get("task-body")
        label = request.form.get("label")
        task_date = datetime.strptime(request.form.get("task_date"), '%Y-%m-%d')
        
        if new_task is not None:
            task = Tasks(user_id=user_id, task_title=task_title, task_body=new_task, task_completed=False, task_date=task_date, task_category=label)
            db.session.add(task)
            db.session.commit()
            msg = "Task successfully created"
            cate = "success"
        else:
            msg = "Task Text is required"
            cate = "error"

    
    return render_template('add-task.html', msg=msg, cate=cate, task_cate=user_task_categories, user_name=user_name)



@app.route('/tasks-list', methods=['GET', 'POST'])
def tasks_list():
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user

    if not current_user.is_authenticated:
       return redirect(url_for('login'))


    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_tasks = Tasks.query.filter_by(user_id=user_id).all()

    if request.method == "POST":
        print("yes")

    
    return render_template('tasks-list.html', msg=msg, cate=cate, user_tasks=user_tasks, user_name=user_name)

@app.errorhandler(404)
def not_found(e):
  return redirect(url_for("index"))