import datetime

from flask_login import UserMixin

from . import db

association_table = db.Table("association_table",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True)
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    todos = db.relationship("ToDo", backref="category", lazy="joined")


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    is_completed = db.Column(db.Boolean, default=False)
    create_date = db.Column(db.Date, default=datetime.date.today())
    deadline = db.Column(db.Date)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    tasks = db.relationship("ToDo", backref=db.backref("user", lazy="joined"))
    categories = db.relationship("Category", secondary=association_table, lazy="subquery",
                                 backref=db.backref("users", lazy="dynamic"))


