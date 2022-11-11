from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (StringField, TextAreaField, PasswordField, SubmitField,
                     SelectField, DateField)
from wtforms.validators import DataRequired, Email, Optional


def get_categories():
    try:
        choices = [(category.id, category.name)
                   for category in current_user.categories]
        choices.append((0, ""))
        return choices
    except AttributeError:
        return 0, ""


class CreateTaskForm(FlaskForm):
    description = TextAreaField("Description of the Task", validators=[DataRequired()])
    category = SelectField("Category", choices=get_categories(),
                           coerce=int)
    deadline = DateField("Deadline (optional)", validators=[Optional()])
    submit = SubmitField("Create Task")

    def populate_obj(self, obj):
        obj.description = self.description.data
        obj.category_id = self.category.data
        obj.deadline = self.deadline.data


class CreateCategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired()])
    submit = SubmitField("Create Category")


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
