from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from .models import User
from wtforms import ValidationError
from wtforms.fields import URLField
from wtforms.validators import DataRequired, Optional


# Registration Form for Users
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

# Login Form for Users
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[('tech', 'Tech'), ('sport', 'Sport'), ('music', 'Music')], validators=[DataRequired()])
    image_url = URLField('Image URL (Optional)', validators=[Optional()])
    video_url = URLField('Video URL (Optional)', validators=[Optional()])
    submit = SubmitField('Submit')

# Edit Post Form for Users and Admins
class EditPostForm(PostForm):
    submit = SubmitField('Update Post')

# Comment Form for Users to Add Comments
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

# Admin Form for Managing Posts
class AdminPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    image_url = StringField('Image URL')
    video_url = StringField('Video URL')
    user_id = SelectField('User', coerce=int)  # Dropdown to select a user (admin can choose any user)
    submit = SubmitField('Create Post')

# Admin Form for Editing Posts
class AdminEditPostForm(AdminPostForm):
    submit = SubmitField('Update Post')

# Admin Form for Managing Users (example: promoting or deleting users)
class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update User')

# Admin Form for Managing Comments (e.g., deleting or flagging)
class AdminCommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    post_id = SelectField('Post', coerce=int)  # Select the post for which the comment belongs to
    submit = SubmitField('Update Comment')

# Form for Admin Login (if needed)
class AdminLoginForm(LoginForm):
    submit = SubmitField('Admin Login')
