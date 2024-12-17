from functools import wraps
from mailbox import Message
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, abort
from .models import Post, User, Comment, db
from .forms import CommentForm, EditPostForm, PostForm
from flask_login import login_required, current_user, login_user
from datetime import datetime
from flask import flash, redirect, url_for, current_app
from flask_mail import Mail
from flask_mail import Message
from flask import current_app  # Adjust based on your project structure


# Blueprints
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)
auth = Blueprint('auth', __name__) 

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Log current_user details for debugging
        current_app.logger.info(f"Admin Check: Current User: {current_user}")
        current_app.logger.info(f"Is Authenticated: {current_user.is_authenticated}")
        
        # Check if the user is authenticated
        if not current_user.is_authenticated:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login page

        # Check if the user is an admin
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin():
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('main.index'))  # Redirect to home or non-admin page

        # User is authenticated and an admin
        return func(*args, **kwargs)
    return decorated_view


# Home Route
@main.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

# Admin Dashboard
@admin.route('/dashboard')
@admin_required
def admin_dashboard():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('admin/dashboard.html', posts=posts)

# Edit Post Route
@admin.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.image_url = form.image_url.data
        post.video_url = form.video_url.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/edit_post.html', form=form, post=post)

# Delete Post Route
@admin.route('/post/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    Comment.query.filter_by(post_id=post.id).delete()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin.admin_dashboard'))

# Post Route - Display a single post and its comments
@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.asc()).all()
    return render_template('post_detail.html', post=post, form=form, comments=comments)

# Add Comment to Post Route
@main.route('/post/<int:post_id>/add_comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash('Please log in to comment', 'error')
        return redirect(url_for('auth.login'))

    content = request.form.get('content')
    if not content:
        flash('Content is required', 'error')
        return redirect(url_for('main.post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    comment = Comment(content=content, post_id=post.id, user_id=session['user_id'])
    db.session.add(comment)
    db.session.commit()
    flash('Comment added successfully!', 'success')
    return redirect(url_for('main.post', post_id=post_id))

@main.route('/')
def home():
    # Fetch the latest 8 posts sorted by timestamp in descending order
    posts = Post.query.order_by(Post.timestamp.desc()).limit(8).all()
    return render_template('index.html', posts=posts)

@main.route('/explore', methods=['GET'])
@main.route('/explore/<category>', methods=['GET'])
def explore(category=None):
    # Fetch posts for each category
    tech_posts = Post.query.filter_by(category='tech').limit(6).all()
    sports_posts = Post.query.filter_by(category='sports').limit(6).all()
    music_posts = Post.query.filter_by(category='music').all()

    # Track which category is selected
    selected_category = category if category in ['tech', 'sports', 'music'] else None

    return render_template(
        'explore.html',
        tech_posts=tech_posts,
        sports_posts=sports_posts,
        music_posts=music_posts,
        selected_category=selected_category
    )

# About Us Page Route
@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create email message
        msg = Message(
            subject=f"New Message from {name}",
            sender=email,  # Use the user's email as the sender
            recipients=[current_app.config['MAIL_DEFAULT_SENDER']],
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )

        try:
            current_app.mail.send(msg)  # Send the message using current_app.mail
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash("An error occurred while sending your message. Please try again.", "danger")
            print(f"Error: {e}")

    return render_template('contact.html')




@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'user')  # Default role is 'user'

        # Validate form inputs
        if not fullname or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=fullname, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Missing email or password'}), 400

        email = data['email']
        password = data['password']
        user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):  # Assuming check_password validates the hashed password
        login_user(user)
        session['user_id'] = user.id
        # Check if the user's role is admin
        is_admin = user.role == 'admin'
        return jsonify({'success': True, 'is_admin': is_admin})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


# Logout Route
@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@admin.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        category = form.category.data
        image_url = form.image_url.data
        video_url = form.video_url.data

        try:
            # Create a new post
            post = Post(
                title=title,
                content=content,
                category=category,
                image_url=image_url,
                video_url=video_url,
                user_id=current_user.id  # Assign the logged-in user's ID
            )
            db.session.add(post)
            db.session.commit()

            flash(f'Your post has been created under the "{category}" category!', 'success')
            return redirect(url_for('admin.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('admin/create_post.html', form=form)


# Admin Manage Comments Route
@admin.route('/comments')
def manage_comments():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))

    comments = Comment.query.all()
    return render_template('admin/manage_comments.html', comments=comments)

@admin.route('/admin/users')
def manage_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        return redirect(url_for('index'))  # Redirect if user doesn't exist or isn't an admin

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


# Admin Dashboard Route
@admin.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('main.login'))  # Redirect to login if not logged in

    user = User.query.get(session['user_id'])
    if not user.is_admin():  # Check if the logged-in user is an admin
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))  # Redirect to the main page if not an admin

    posts = Post.query.all()  # Fetch all posts for the admin dashboard
    return render_template('admin/dashboard.html', posts=posts)  # Render admin dashboard template

# Like a Comment Route
@main.route('/comment/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if 'user_id' not in session:
        flash('Please log in to like', 'error')
        return redirect(url_for('main.login'))

    if comment.likes.filter_by(user_id=session['user_id']).first():
        flash('You have already liked this comment', 'warning')
    else:
        comment.likes.append(User.query.get(session['user_id']))
        db.session.commit()
        flash('You liked the comment!', 'success')

    return redirect(url_for('main.post', post_id=comment.post_id))

# Dislike a Comment Route
@main.route('/comment/<int:comment_id>/dislike', methods=['POST'])
def dislike_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if 'user_id' not in session:
        flash('Please log in to dislike', 'error')
        return redirect(url_for('main.login'))

    if comment.dislikes.filter_by(user_id=session['user_id']).first():
        flash('You have already disliked this comment', 'warning')
    else:
        comment.dislikes.append(User.query.get(session['user_id']))
        db.session.commit()
        flash('You disliked the comment!', 'success')

    return redirect(url_for('main.post', post_id=comment.post_id))

# Add Emoji to Comment Route
@main.route('/comment/<int:comment_id>/emoji', methods=['POST'])
def add_emoji_to_comment(comment_id):
    emoji = request.form.get('emoji')
    if emoji not in ['😀', '😢', '😡', '❤️']:
        flash('Invalid emoji', 'error')
        return redirect(url_for('main.post', post_id=comment_id))

    comment = Comment.query.get_or_404(comment_id)
    comment.emojis.append(emoji)
    db.session.commit()
    flash(f'You added the emoji: {emoji}', 'success')
    return redirect(url_for('main.post', post_id=comment.post_id))

# API to Get Comments for a Post
@main.route('/post/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = [{'content': c.content, 'timestamp': c.timestamp} for c in post.comments]
    return jsonify(comments)

@main.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@admin.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted successfully.", "success")
    else:
        flash("User not found.", "error")
    return redirect(url_for('admin.manage_users'))


@admin.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('admin.manage_comments'))


@main.route('/category/<string:category>')
def category(category):
    # Fetch posts belonging to the specified category
    category_posts = Post.query.filter_by(category=category).all()
    if not category_posts:
        category_posts = []

    return render_template('category.html', category=category, posts=category_posts)
