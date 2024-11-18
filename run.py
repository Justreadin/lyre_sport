from app import create_app
from app.models import User, Post
from app import db  # Ensure db is imported from the app module

app = create_app()

@app.shell_context_processor
def make_shell_context():
    # Return the db, User, and Post models to the shell context
    return {'db': db, 'User': User, 'Post': Post}

if __name__ == '__main__':
    # Running the app in debug mode for development
    app.run(debug=True)
