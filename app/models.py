from flask_bcrypt import Bcrypt
from . import db
from datetime import datetime
from flask_login import UserMixin

bcrypt = Bcrypt()  # Corrected the variable name
from datetime import datetime
from flask_login import UserMixin
from . import bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='user')  # Role: 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Password management
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Check if user is admin
    def is_admin(self):
        return self.role == 'admin'

    # Relationships
    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    video_url = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=False)  # Stores category as a string
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')

    comments = db.relationship('Comment', back_populates='post', lazy=True)

    # Add a timestamp column
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Define the allowed categories as a class-level constant
    ALLOWED_CATEGORIES = ['sport', 'tech', 'music']

    def __init__(self, title, content, image_url=None, video_url=None, category=None, user_id=None):
        if category not in Post.ALLOWED_CATEGORIES:  # Validate the category
            raise ValueError(f"Invalid category. Must be one of: {', '.join(Post.ALLOWED_CATEGORIES)}")
        self.title = title
        self.content = content
        self.image_url = image_url
        self.video_url = video_url
        self.category = category
        self.user_id = user_id



# Association tables for likes and dislikes
comment_likes = db.Table(
    'comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True)
)

comment_dislikes = db.Table(
    'comment_dislikes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True)
)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship with Post
    post = db.relationship('Post', back_populates='comments')
    
    # Relationship with User
    user = db.relationship('User', back_populates='comments')

    # Relationships for likes and dislikes
    likes = db.relationship('User', secondary=comment_likes, backref='liked_comments')
    dislikes = db.relationship('User', secondary=comment_dislikes, backref='disliked_comments')

    # A list to store emojis
    emojis = db.Column(db.PickleType, default=[])

