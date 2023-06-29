from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import os
import psycopg2
from forms import AddUserForm, LoginForm, FeedbackForm


load_dotenv(override=True)
pw = os.getenv("pw")
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{pw}@localhost/feedback'

app.app_context().push()


app.config['SECRET_KEY'] = "HELLO123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()


@app.route('/')
def register_redirect():
    return redirect('/register')


@app.route('/register')
def register_form():
    form = AddUserForm()
    return render_template('register-form.html', form=form)


@app.route('/register', methods=['POST'])
def submit_reg_form():
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password,
                                 email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(f'/users/{username}')
    else:
        return render_template('register-form.html', form=form)


@app.route('/login')
def log_in():
    form = LoginForm()
    return render_template('login-form.html', form=form)


@app.route('/login', methods=['POST'])
def submit_login_form():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            session['user_id'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Bad name/password']

    return render_template('login-form.html', form=form)


@app.route('/users/<username>')
def secret_page(username):
    if "user_id" not in session or username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")
    else:
        user = User.query.get(username)
        return render_template('user-info.html', user=user)


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if "user_id" not in session or username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")
    user = User.query.get_or_404(username)
    # feedbacks = Feedback.query.filter_by(username=username).all()
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    return redirect("/")


@app.route('/users/<username>/feedback/add')
def feedback_form(username):
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    if "user_id" not in session or username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")
    return render_template("feedback-form.html", form=form)


@app.route('/users/<username>/feedback/add', methods=["POST"])
def send_feedback(username):
    if "user_id" not in session or username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")

    form = FeedbackForm()
    if form.validate_on_submit():
        new_feedback = Feedback(title=form.title.data,
                                content=form.content.data,
                                username=username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f"/users/{username}")


@app.route('/feedback/<feedbacks_id>/update')
def edit_feedback(feedbacks_id):
    feedback = Feedback.query.get(feedbacks_id)
    form = FeedbackForm(obj=feedback)
    if "user_id" not in session or feedback.username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")
    return render_template("feedback-form.html", form=form)


@app.route('/feedback/<feedbacks_id>/update', methods=['POST'])
def submit_edit(feedbacks_id):
    feedback = Feedback.query.get(feedbacks_id)
    form = FeedbackForm()
    if "user_id" not in session or feedback.username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")
    feedback.title = form.title.data
    feedback.content = form.content.data
    db.session.add(feedback)
    db.session.commit()
    return redirect(f'/users/{feedback.username}')


@app.route('/feedback/<feedbacks_id>/delete', methods=['POST'])
def delete_feedback(feedbacks_id):
    feedback = Feedback.query.get(feedbacks_id)
    if "user_id" not in session or feedback.username != session['user_id']:
        flash("You must be logged in to view this person!")
        return redirect("/login")
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{feedback.username}')
