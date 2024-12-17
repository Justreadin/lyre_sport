from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Justreading.1m@localhost/sport_blog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"  # or "secure cookies" for production
    SESSION_COOKIE_SECURE = False 
    REMEMBER_COOKIE_DURATION= timedelta(days=7)
    MAIL_SERVER= 'smtp.gmail.com'  # Change this if using another email provider
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'Favour'  # Replace with your email
    MAIL_PASSWORD = 'fjmg huky hqck etwd'  # Replace with your email password
    MAIL_DEFAULT_SENDER = 'your_email@example.com'
    MAIL_RECIPIENT = 'dave.400g@gmail.com'
