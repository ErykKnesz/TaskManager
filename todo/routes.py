from datetime import date
from functools import wraps
import os

from flask import render_template, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.exc import IntegrityError

from todo import app, db
from todo.models import ToDo, Category, User
from todo.forms import CreateTaskForm, CreateCategoryForm, UserForm, get_categories

login_manager = LoginManager()
login_manager.init_app(app)

# def admin_only(func):
#     @wraps(func)
#     def inner(*args, **kwargs):
#         try:
#             if current_user.id == 1:
#                 return func(*args, **kwargs)
#         except AttributeError:
#             return abort(403)
#     return inner


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user


@app.route('/register', methods=["GET", "POST"])
def register():
    form = UserForm()
    if request.method == "POST" and form.validate_on_submit():
        pass_hash = generate_password_hash(form.data["password"],
                                           method='pbkdf2:sha256',
                                           salt_length=8)
        if User.query.filter_by(email=form.data['email']).first():
            flash('This email address is already used')
            return redirect(url_for('login'))
        try:
            user = User(
                email=form.data["email"],
                password=pass_hash,
            )
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash('Unexpected Error. Please try again.')
        flash('New User Created!')
        return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route('/login',  methods=["GET", "POST"])
def login():
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.data['email']).first()
            if user:
                if check_password_hash(user.password, form.data["password"]):
                    login_user(user)
                    return redirect(url_for('home'))
                flash('Wrong password.')
                return redirect(url_for('login'))
            flash('Email address not found.')
            return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/")
def home():
    tasks = db.session.query(ToDo).filter_by(user_id=current_user.get_id())
    task_form = CreateTaskForm()
    task_form.category.choices = get_categories()
    category_form = CreateCategoryForm()
    return render_template("home.html", tasks=tasks,
                           task_form=task_form, category_form=category_form)


@login_required
@app.route("/add-task", methods=["GET", "POST"])
def add_task():
    form = CreateTaskForm()
    form.category.choices = get_categories()
    if request.method == "POST":
        user = db.session.query(User).get(current_user.get_id())
        category = db.session.query(Category).get(form.data["category"])
        if form.validate():
            flash("New Task Created!", "success")
            task = ToDo(description=form.data["description"], user=user,
                        category=category)
            db.session.add(task)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("task.html", task_form=form)


@login_required
@app.route("/add-category", methods=["GET", "POST"])
def add_category():
    form = CreateCategoryForm()
    if request.method == "POST":
        user = db.session.query(User).get(current_user.get_id())
        if form.validate():
            name = form.data["name"].lower()
            category_in_db = db.session.query(Category).filter_by(
                name=name).first()
            if category_in_db:
                user.categories.append(category_in_db)
            else:
                category = Category(name=name, user=user)
                db.session.add(category)
            db.session.commit()
            flash("New Category Created!", "success")
    categories = db.session.query(Category).filter_by(
        user_id=current_user.get_id())
    return render_template("category.html", category_form=form,
                           categories=categories)
