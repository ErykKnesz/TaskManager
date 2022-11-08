from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email


def get_categories():
    try:
        return [(category.id, category.name)
                for category in current_user.categories]
    except AttributeError:
        return ""


class CreateTaskForm(FlaskForm):
    description = TextAreaField("Description of the Task", validators=[DataRequired()])
    category = SelectField("Category", choices=get_categories(),
                           coerce=int)
    submit = SubmitField("Create Task")


class CreateCategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired()])
    submit = SubmitField("Create Category")


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
