from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField

class AddUserForm(FlaskForm):

    username = StringField("username")
    password = PasswordField("password")
    email = EmailField("email")
    first_name = StringField("first_name")
    last_name = StringField("last_name")


class LoginForm(FlaskForm):

    username = StringField("username")
    password = PasswordField("password")