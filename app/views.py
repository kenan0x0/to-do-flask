import os, logging 
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

from app import app, lm, db, bc
from app.models import Users, Tasks

from datetime import datetime
import base64
import hashlib

@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Decide which profile image will be shown
def user_profile_image(db_image, email):
    if db_image is None:
        GRAVATAR_ENDPOINT = "https://www.gravatar.com/avatar/"
        user_image = (GRAVATAR_ENDPOINT+ hashlib.md5(email.encode("utf-8")).hexdigest())
        return user_image
    else:
        return db_image

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

        image_content = None
        profile_image = request.files.get("register-profile-image")
        if profile_image.filename:
            image_content = f"data:{profile_image.content_type};charset=utf-8;base64,{base64.b64encode(profile_image.read()).decode('utf-8')}"

        user = Users.query.filter_by(user=username).first()
        user_by_email = Users.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
            cate = 'error'

        else:         
            pw_hash = bc.generate_password_hash(password)
            user = Users(username, email, pw_hash, image_content, datetime.now().date())
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
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    account_creation = Users.query.filter_by(email=current_user.email).first().creation_time
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)
    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_tasks = Tasks.query.filter_by(user_id=user_id).all()


    tasks_finished = 0
    tasks_ongoing = 0
    for task in user_tasks:
        if task.task_completed:
            tasks_finished += 1
        else:
            tasks_ongoing += 1
    tasks_total = len(user_tasks)

    calendar_tasks = [[task.task_date.strftime("%m/%d/%Y").replace("/","-"), task.task_title, task.task_body, task.id] for task in user_tasks]
    
    return render_template('index.html', user_name=user_name, calendar_tasks=calendar_tasks, prof_pic=prof_pic, tasks_total=tasks_total, tasks_finished=tasks_finished, tasks_ongoing=tasks_ongoing, account_creation=account_creation)

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    msg = None
    cate = None

    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)
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

    
    return render_template('add-task.html', msg=msg, cate=cate, task_cate=user_task_categories, user_name=user_name, prof_pic=prof_pic)



@app.route('/tasks-list', methods=['GET', 'POST'])
def tasks_list():
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)

    if not current_user.is_authenticated:
       return redirect(url_for('login'))


    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_tasks = Tasks.query.filter_by(user_id=user_id).all()
    
    return render_template('tasks-list.html', msg=msg, cate=cate, user_tasks=user_tasks, user_name=user_name, prof_pic=prof_pic)



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)
    user_obj = Users.query.filter_by(email=current_user.email).first()

    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "pas":
            pswd = request.form.get("password")
            pswd_conf = request.form.get("confirm-password")
            if pswd == pswd_conf:
                pw_hash = bc.generate_password_hash(pswd)
                user_obj.password = pw_hash
                db.session.commit()
        else:
            usrname = request.form.get("username")
            full_name = request.form.get("full_name")
            city = request.form.get("city")
            
            image_content = None
            profile_img = request.files.get("setting-profile-image")
            if profile_img.filename:
                image_content = f"data:{profile_img.content_type};charset=utf-8;base64,{base64.b64encode(profile_img.read()).decode('utf-8')}"

            if usrname:
                exists = Users.query.filter_by(user=usrname).first()
                if not exists:
                    user_obj.user = usrname
            
            if city:
                user_obj.city = city

            if full_name:
                user_obj.full_name = full_name

            if image_content:
                user_obj.user_image = image_content

            db.session.commit()

    
    return render_template('settings.html', msg=msg, cate=cate, user_name=user_name, prof_pic=prof_pic, user=user_obj)


@app.route("/handleTasks/<task_id>/<req_type>", methods=['GET', 'POST'])
def handle_tasks(task_id, req_type):
    if req_type == "fk":
        task_obj = Tasks.query.filter_by(id=task_id).first()
        task_obj.task_completed = True
        db.session.commit()
    elif req_type == "ro":
        task_obj = Tasks.query.filter_by(id=task_id).first()
        task_obj.task_completed = False
        db.session.commit()
    elif req_type == "fd":
        task_obj = Tasks.query.filter_by(id=task_id).delete()
        db.session.commit()
    elif req_type == "edit":
        new_title = request.form.get("task_title")
        new_body = request.form.get("task_body")
        new_category = request.form.get("task_category")
        new_date = datetime.strptime(request.form.get("task_date"), '%Y-%m-%d').date()
        task_obj = Tasks.query.filter_by(id=task_id).first()
        
        task_obj.task_title = new_title
        task_obj.task_body = new_body
        task_obj.task_category = new_category
        task_obj.task_date = new_date
        db.session.commit()

    return redirect(url_for("tasks_list"))


@app.route("/del-account/<u_id>", methods=['GET', 'POST'])
def handle_deletions(u_id):
    Tasks.query.filter_by(user_id=int(u_id)).delete()
    Users.query.filter_by(id=int(u_id)).delete()
    db.session.commit()

    return redirect(url_for("logout"))

@app.errorhandler(404)
def not_found(e):
  return redirect(url_for("index"))