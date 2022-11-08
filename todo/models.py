from flask_login import UserMixin

from . import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    todos = db.relationship("ToDo", backref='category', lazy="joined")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    tasks = db.relationship('ToDo', backref=db.backref("user", lazy="joined"))
    categories = db.relationship('Category', backref=db.backref("user", lazy="joined"))


