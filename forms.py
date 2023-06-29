from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField

class AddUserForm(FlaskForm):

    username = StringField("Username")
    password = PasswordField("Password")
    email = EmailField("Email")
    first_name = StringField("First Name")
    last_name = StringField("Last Name")


class LoginForm(FlaskForm):

    username = StringField("Username")
    password = PasswordField("Password")


class FeedbackForm(FlaskForm):

    title = StringField("Title")
    content = StringField("Content")