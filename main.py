from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from form import LoginForm, PostForm, RegisterForm, UrlForm
from api import SheetyApi
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
data_base = os.getenv("DATABASE_URL")
if data_base and data_base.startswith("postgres://"):
    data_base = data_base.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = data_base
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# login
login_manager = LoginManager()
login_manager.init_app(app)
# Database
db = SQLAlchemy(app)
base = declarative_base()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


class Users(UserMixin, db.Model, base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    child = relationship("SheetEndpoint", backref="user")


class SheetEndpoint(db.Model, base):
    __tablename__ = "sheet_endpoint"
    id = db.Column(db.Integer, primary_key=True)
    sheet_endpoint = db.Column(db.Text, nullable=False)
    current_number = db.Column(db.Integer, )
    user_id = db.Column(db.Integer, ForeignKey("users.id"))


db.create_all()


@app.route("/")
def home():
    year = datetime.datetime.now().year
    return render_template("index.html", year=year)


@app.route("/register", methods=["POST", "GET"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user_exist = Users.query.filter_by(email=register_form.email.data.strip()).first()
        if user_exist:
            flash("Email entered already exists, login rather")
            return redirect(url_for("login"))
        else:
            hashed_password = generate_password_hash(password=register_form.password.data.strip(), method="pbkdf2:sha256",
                                                     salt_length=16)
            new_user = Users(email=register_form.email.data.strip(),
                             password=hashed_password,
                             first_name=register_form.first_name.data.strip().lower().title(),
                             last_name=register_form.second_name.data.strip().lower().title())
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        return redirect(url_for("posts"))
    return render_template("register.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = Users.query.filter_by(email=login_form.email.data.strip()).first()
        if user:
            if check_password_hash(pwhash=user.password, password=login_form.password.data.strip()):
                login_user(user)
            else:
                flash("Incorrect password, try again")
        else:
            flash("Email entered does not exist, register rather")
            return redirect(url_for("register"))
        return redirect(url_for("posts"))
    return render_template("login.html", form=login_form)


def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.id == 1 and current_user.is_authenticated:
            return function(*args, **kwargs)

    return wrapper_function


@app.route("/sheet-url", methods=["POST", "GET"])
@login_required
@admin_only
def url_getter():
    url_form = UrlForm()
    if url_form.validate_on_submit():
        new_url = SheetEndpoint(sheet_endpoint=url_form.url.data, current_number=1,
                                user_id=current_user.id)
        db.session.add(new_url)
        db.session.commit()
    return render_template("url.html", form=url_form)


@app.route("/post-data", methods=["GET", "POST"])
@login_required
def posts():
    post_form = PostForm()
    user = Users.query.get(current_user.id)
    if post_form.validate_on_submit():
        sheety_api = SheetyApi(family=post_form.family.data,
                               genus=post_form.genus.data, species=post_form.species.data,
                               authority=post_form.authority.data, localName=post_form.local_name.data,
                               language=post_form.language.data,
                               size_file=post_form.size_of_file.data,
                               country=post_form.country.data,
                               scribe=f"{user.first_name.lower().title()} {user.last_name.lower().title()}",
                               size_tiff=post_form.size_tiff.data,
                               )

        try:
            sheety_api.post_data()
        except ConnectionError:
            flash("Poor Connection")
        else:
            return redirect(url_for("posts"))
    return render_template("posts.html", form=post_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
