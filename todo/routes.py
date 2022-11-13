from datetime import date

from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (login_user, LoginManager, login_required,
                         current_user, logout_user)
from sqlalchemy.exc import IntegrityError

from todo import app, db
from todo.models import ToDo, Category, User
from todo.forms import (CreateTaskForm, CreateCategoryForm, UserForm,
                        get_categories)

login_manager = LoginManager()
login_manager.init_app(app)


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
            flash('This email address is already used', "info")
            return redirect(url_for('login'))
        try:
            user = User(
                email=form.data["email"],
                password=pass_hash,
            )
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash('Unexpected Error. Please try again.', "info")
        flash('New User Created!', "success")
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
                flash('Wrong password.', "info")
                return redirect(url_for('login'))
            flash('Email address not found.', "info")
            return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/")
def home():
    tasks = db.session.query(ToDo).filter_by(
        user_id=current_user.get_id())
    if 'sort' in request.args.keys():
        if request.args['sort'] == 'deadline':
            tasks = tasks.order_by(ToDo.deadline.desc())
        elif request.args['sort'] == 'create_date':
            tasks = tasks.order_by(ToDo.create_date.desc())
        elif request.args['sort'] == 'completed':
            tasks = tasks.order_by(ToDo.is_completed.desc())
        elif request.args['sort'] == 'not completed':
            tasks = tasks.order_by(ToDo.is_completed.asc())
    elif 'filter' in request.args.keys():
        if request.args['filter'] == 'deadline':
            tasks = tasks.filter_by(deadline=date.today())
        elif request.args['filter'] == 'create_date':
            tasks = tasks.filter_by(create_date=date.today())
        elif request.args['filter'] == 'completed':
            tasks = tasks.filter_by(is_completed=True)
        elif request.args['filter'] == 'not completed':
            tasks = tasks.filter_by(is_completed=False)
    else:
        tasks = tasks.order_by(ToDo.category_id)
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
                        category=category, deadline=form.data['deadline'])
            db.session.add(task)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("task.html", task_form=form)


@login_required
@app.route("/delete-task/<int:task_id>")
def delete_task(task_id):
    task = db.session.query(ToDo).get(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task Deleted!", "success")
    return redirect(url_for("home"))


@login_required
@app.route("/update-task/<int:task_id>", methods=["GET", "POST"])
def update_task(task_id):
    task = db.session.query(ToDo).get(task_id)
    form = CreateTaskForm()
    form.category.choices = get_categories(task.category)
    if request.method == "POST":
        if form.validate_on_submit():
            form.populate_obj(task)
            db.session.commit()
            flash("Task Updated!", "success")
        return redirect(url_for("home"))
    form.deadline.data = task.deadline
    form.category.data = task.category
    form.description.data = task.description
    return render_template("edit_task.html",
                           task_form=form,
                           task_id=task_id)


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
                category = Category(name=name)
                db.session.add(category)
                user.categories.append(category)
                category.users.append(user)
            db.session.commit()
            flash("New Category Created!", "success")
    categories = db.session.query(Category).filter(Category.users.any(
        User.id == current_user.get_id()))
    return render_template("category.html", category_form=form,
                           categories=categories)


@login_required
@app.route("/complete-task/<int:task_id>", methods=["GET"])
def complete_task(task_id):
    task = db.session.query(ToDo).get(task_id)
    task.is_completed = True if not task.is_completed else False
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('home'))
