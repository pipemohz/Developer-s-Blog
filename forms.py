from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.core import Label
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(),Email(message="Not a valid email account")])
    password = PasswordField(label="Password", validators=[DataRequired(),Length(min=5, message="Password must have at least 5 characters")])
    name = StringField(label="Name", validators=[DataRequired()])
    submit = SubmitField(label="Create user")

class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(),Email(message="Input a valid email account")])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Log in")

class CommentForm(FlaskForm):
    body = CKEditorField(label="Comment", validators=[DataRequired()])
    submit = SubmitField(label="Create comment")