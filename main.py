import os
from datetime import datetime 
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email

from functools import wraps

year = datetime.now().year
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login manager
login = LoginManager()
login.init_app(app)

# Gravatar

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# CONFIGURE TABLES

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    commentaries = relationship("Commentary", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # author = db.Column(db.String(250), nullable=False)
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commentaries = relationship("Commentary", back_populates="post")


class Commentary(db.Model):
    __tablename__ = "commentaries"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = relationship("User", back_populates="commentaries")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post = relationship("BlogPost", back_populates="commentaries")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))

db.create_all()


def create_user(form: RegisterForm):
    user = User(
        name=form.name.data,
        email=form.email.data,
        password=generate_password_hash(
            form.password.data, method='pbkdf2:sha256', salt_length=8)
    )

    db.session.add(user)
    db.session.commit()


def get_user(form: RegisterForm):
    return db.session.query(User).filter_by(email=form.email.data).first()


def create_comment(form: CommentForm, id: int):
    comment = Commentary(
        text=form.body.data,
        author=current_user,
        post=db.session.query(BlogPost).get(id)
    )
    db.session.add(comment)
    db.session.commit()

# def load_comments(post:BlogPost, id:int) -> List:
#     return db.session.query(Commentary).filter_by(post.id=id).all()


def admin_only(function):
    @wraps(function)
    def function_wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return function(*args, **kwargs)
        else:
            return abort(403, description="Permission denied: Only Admin user can access this route.")

    return function_wrapper


def logged_in(function):
    @wraps(function)
    def function_wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        else:
            flash(message="Login required.")
            return redirect(url_for('login'))
    return function_wrapper


@login.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts, year=year)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if get_user(form) == None:
            create_user(form)
            user = get_user(form)
            login_user(user)
            print(current_user)
            return redirect(url_for('get_all_posts'))
        else:
            flash(message="The user is already registered. Try login instead.")
            return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if get_user(form) == None:
            flash(message="The user does not exist.")
        elif not check_password_hash(get_user(form).password, form.password.data):
            flash(message="The password does not match.")
        else:
            user = get_user(form)
            login_user(user)
            # print(current_user.is_authenticated)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    # print(current_user)
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    # commentaries = load_comments(requested_post, post_id)
    if form.validate_on_submit():
        if current_user.is_anonymous:
            flash(message="You must log in for post a comment.")
            return redirect(url_for('login'))
        else:
            create_comment(form, post_id)
            return redirect(url_for('get_all_posts'))

    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=['POST', 'GET'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=['GET','POST'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
