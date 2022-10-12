import os, logging 
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

from app import app, lm, db, bc
from app.models import Users, Tasks, Notes, Friends, Notifications

from datetime import datetime, timedelta
import base64
import hashlib
import time

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
    user_notes = len(Notes.query.filter_by(user_id=user_id).all())
    notifications = Notifications.query.filter_by(user_id=user_id).all()


    tasks_finished = 0
    tasks_ongoing = 0
    for task in user_tasks:
        if task.task_completed:
            tasks_finished += 1
        else:
            tasks_ongoing += 1
    tasks_total = len(user_tasks)

    calendar_tasks = [[task.task_date.strftime("%m/%d/%Y").replace("/","-"), task.task_title, task.task_body, task.id] for task in user_tasks]
    
    return render_template('index.html', user_name=user_name, calendar_tasks=calendar_tasks, prof_pic=prof_pic, tasks_total=tasks_total, tasks_finished=tasks_finished, tasks_ongoing=tasks_ongoing, account_creation=account_creation, user_notes=user_notes, notifications=notifications)

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    msg = None
    cate = None

    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)
    user_task_categories = [task.task_category for task in Tasks.query.filter_by(user_id=user_id).all()]
    notifications = Notifications.query.filter_by(user_id=user_id).all()

    if request.method == "POST":
        task_title = request.form.get("task-title")
        new_task = request.form.get("task-body")
        label = request.form.get("label")
        task_date = datetime.strptime(request.form.get("task_date"), '%Y-%m-%d').date()        

        
        if new_task is not None:
            task = Tasks(user_id=user_id, task_title=task_title, task_body=new_task, task_completed=False, task_date=task_date, task_category=label)
            db.session.add(task)
            db.session.commit()
            msg = "Task successfully created"
            cate = "success"
        else:
            msg = "Task Text is required"
            cate = "error"

    
    return render_template('add-task.html', msg=msg, cate=cate, task_cate=user_task_categories, user_name=user_name, prof_pic=prof_pic, notifications=notifications)



@app.route('/tasks-list', methods=['GET', 'POST'])
def tasks_list():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))
    
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)


    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_tasks = Tasks.query.filter_by(user_id=user_id).all()
    today_date = datetime.now().date()
    notifications = Notifications.query.filter_by(user_id=user_id).all()
    
    return render_template('tasks-list.html', msg=msg, cate=cate, user_tasks=user_tasks, user_name=user_name, prof_pic=prof_pic, notifications=notifications, today_date=today_date)


@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))
    
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)


    user_id = Users.query.filter_by(email=current_user.email).first().id
    user_notes = Notes.query.filter_by(user_id=user_id).all()
    notifications = Notifications.query.filter_by(user_id=user_id).all()

    if request.method == "POST":
        note_title = request.form.get("note-title")
        note_body = request.form.get("note-body")
        note_color = request.form.get("note-color")
        
        created_note = Notes(user_id=user_id, note_title=note_title, note_body=note_body, note_color_hex=note_color)
        db.session.add(created_note)
        db.session.commit()
        return redirect(request.referrer)
    
    return render_template('notes.html', msg=msg, cate=cate, user_name=user_name, prof_pic=prof_pic, notes=user_notes, notifications=notifications)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))
    
    
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)
    user_obj = Users.query.filter_by(email=current_user.email).first()
    user_id = Users.query.filter_by(email=current_user.email).first().id
    notifications = Notifications.query.filter_by(user_id=user_id).all()


    account_discoverable = user_obj.acc_privacy
    todos_discoverable = user_obj.todos_privacy
    notes_discoverable = user_obj.notes_privacy
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "pas":
            pswd = request.form.get("password")
            pswd_conf = request.form.get("confirm-password")
            if pswd == pswd_conf:
                pw_hash = bc.generate_password_hash(pswd)
                user_obj.password = pw_hash
                db.session.commit()
        
        elif action == "privacy":
            acc_toggle = True if request.form.get("acc-toggle") == "yes" else False
            todos_toggle = True if request.form.get("todos-toggle") == "yes" else False
            notes_toggle = True if request.form.get("notes-toggle") == "yes" else False
            
            user_obj.todos_privacy = todos_toggle
            user_obj.notes_privacy = notes_toggle
            user_obj.acc_privacy = acc_toggle
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

    return render_template('settings.html', msg=msg, cate=cate, user_name=user_name, prof_pic=prof_pic, user=user_obj, notes_discoverable=notes_discoverable, account_discoverable=account_discoverable, todos_discoverable=todos_discoverable, notifications=notifications)


@app.route("/friends", methods=['GET', 'POST'])
def friends():
    if not current_user.is_authenticated:
       return redirect(url_for('login'))

    
    msg = None
    cate = None
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)


    # Used to remove exisitng friends from the search results
    checker_list = []


    user_id = Users.query.filter_by(email=current_user.email).first().id

    notifications = Notifications.query.filter_by(user_id=user_id).all()

    friends_query_1 = Friends.query.filter_by(user_1=user_id).all()
    friends_query_2 = Friends.query.filter_by(user_2=user_id).all()
    friends_query = friends_query_1 + friends_query_2
    friends_list = []
    for friend in friends_query:
        friend_id = None
        if friend.user_1 == user_id:
            friend_id = friend.user_2
        else:
            friend_id = friend.user_1

        friend_item = [Users.query.filter_by(id=friend_id).first(), friend.friends_since, friend.id]

        friends_list.append(friend_item)
    
    for person in friends_list:
        person[0].user_image = user_profile_image(db_image=person[0].user_image, email=person[0].email)


    friend_count = len(friends_list)
    for person in friends_list:
        checker_list.append(person[0])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "search":
            start_time = time.time()
            intermediate_results = []
            final_results = []

            search_term = request.form.get("search-term")
            search_term = "%{}%".format(search_term)
            query_1 = Users.query.filter(Users.user.like(search_term)).all()
            query_2 = Users.query.filter(Users.email.like(search_term)).all()
            query_results = query_1 + query_2
            query_results = list(dict.fromkeys(query_results))
            for person in query_results:
                person.user_image = user_profile_image(db_image=person.user_image, email=person.email)

            # Remove yourself
            for person in query_results:
                if person.id == user_id:
                    query_results.remove(person)
                    break
            
            for person in query_results:
                if person.acc_privacy:
                    intermediate_results.append(person)

            for person in intermediate_results:
                if person not in checker_list:
                    final_results.append(person)

            end_time = time.time()
            elapsed_time = round((end_time - start_time), 3)
            
            return render_template("friends.html", msg=msg, cate=cate, user_name=user_name, prof_pic=prof_pic, final_results=final_results, friends_list=friends_list, friend_count=friend_count, notifications=notifications, elapsed_time=elapsed_time)

    return render_template("friends.html", msg=msg, cate=cate, user_name=user_name, prof_pic=prof_pic, friends_list=friends_list, friend_count=friend_count, notifications=notifications)

# Add friends handler
@app.route("/add-friend/<friend_id>", methods=['GET', 'POST'])
def add_friend(friend_id):
    user_id = Users.query.filter_by(email=current_user.email).first().id
    initiator = Users.query.filter_by(email=current_user.email).first().user
    add_date = datetime.today().date()

    friend_relation = Friends(user_1=user_id, user_2=friend_id, friends_since=add_date)
    db.session.add(friend_relation)
    db.session.commit()

    notification_body = f"User {initiator} has added you to their friends list!"
    notification_date = datetime.now().replace(microsecond=0) + timedelta(hours=2)
    notification_obj = Notifications(user_id=friend_id, notification=notification_body, notification_date=notification_date)
    db.session.add(notification_obj)
    db.session.commit()

    return redirect(url_for("friends"))

# Delete friends handler
@app.route("/del-friend/<friend_relation_id>", methods=['GET', 'POST'])
def del_friend(friend_relation_id):
    friendship_obj = Friends.query.filter_by(id=friend_relation_id).delete()
    db.session.commit()

    return redirect(url_for("friends"))


# Delete notifications handler
@app.route("/delete-notification/<notification_id>", methods=['GET', 'POST'])
def del_notification(notification_id):
    notification_obj = Notifications.query.filter_by(id=notification_id).delete()
    db.session.commit()

    return redirect(request.referrer)

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
    Friends.query.filter_by(user_1=int(u_id)).delete()
    Friends.query.filter_by(user_2=int(u_id)).delete()
    Notes.query.filter_by(user_id=int(u_id)).delete()
    Tasks.query.filter_by(user_id=int(u_id)).delete()
    Users.query.filter_by(id=int(u_id)).delete()
    db.session.commit()

    return redirect(url_for("logout"))

@app.route("/del-note/<note_id>", methods=['GET', 'POST'])
def handle_note_deletions(note_id):
    Notes.query.filter_by(id=int(note_id)).delete()
    db.session.commit()
    return redirect(url_for("notes"))

@app.errorhandler(404)
def not_found(e):
    if not current_user.is_authenticated:
       return redirect(url_for('login'))
    user_name = Users.query.filter_by(email=current_user.email).first().user
    prof_pic = Users.query.filter_by(email=current_user.email).first().user_image
    prof_pic = user_profile_image(db_image=prof_pic, email=current_user.email)
    return render_template("404.html", user_name=user_name, prof_pic=prof_pic)