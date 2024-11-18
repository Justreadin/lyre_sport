from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from .models import Post, User, Comment, db  # Added Comment model here
from .forms import CommentForm, EditPostForm  # Ensure EditPostForm is defined in forms.py
from . import bcrypt  # Corrected variable name from `bcript` to `bcrypt`

# Define the main and auth blueprints
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# Main Routes
@main.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()  # Ensure CommentForm is defined in forms.py
    return render_template('post.html', post=post, form=form)

@main.route('/post/new', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash('Please log in to create a post', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        new_post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_post.html')

@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if 'user_id' not in session or session['user_id'] != post.user_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
    
    form = EditPostForm(obj=post)  # Bind form to the post object
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('main.post', post_id=post.id))

    return render_template('edit_post.html', form=form, post=post)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if 'user_id' not in session or session['user_id'] != post.user_id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))

    # Delete associated comments first
    Comment.query.filter_by(post_id=post.id).delete()

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('main.index'))

# Auth Routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

# Add a route to post a comment
@main.route('/post/<int:post_id>/add_comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash('Please log in to comment', 'error')
        return redirect(url_for('auth.login'))

    content = request.form.get('content')  # Retrieve content from form data
    if not content:
        flash('Content is required', 'error')
        return redirect(url_for('main.post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    comment = Comment(content=content, post_id=post.id, user_id=session['user_id'])
    db.session.add(comment)
    db.session.commit()
    flash('Comment added successfully!', 'success')
    return redirect(url_for('main.post', post_id=post_id))


# Route to fetch comments for a post
@main.route('/post/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.asc()).all()

    comments_data = [
        {
            'username': comment.user.username,
            'content': comment.content,
            'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for comment in comments
    ]
    return jsonify(comments_data)
