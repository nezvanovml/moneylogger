import os
import yaml
import pathlib
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from celery import Celery


# reading configuration from file
BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / 'config' / 'config.yaml'

def get_config(path):
    with open(path) as f:
        print(f"Loading setting from: {path}")
        config = yaml.safe_load(f)
    return config

config = get_config(config_path)

#initialize flaskapp object
app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
app.config['UPLOAD_FOLDER'] = '/srv/downloads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', None)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["postgres"]["user"]}:{os.environ.get("POSTGRES_PASSWORD", "")}@{config["postgres"]["host"]}:{config["postgres"]["port"]}/{config["postgres"]["database"]}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['CELERY_BROKER_URL'] = 'redis://moneylogger_redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://moneylogger_redis:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

app.config['MAIL_SERVER'] = config["email"]["host"]
app.config['MAIL_PORT'] = config["email"]["port"]
app.config['MAIL_USE_SSL'] = config["email"]["use_ssl"]
app.config['MAIL_USERNAME'] = config["email"]["login"]
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD", "")
mail = Mail(app)


userxrole = db.Table('userxrole',
                         db.Column('user', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('role', db.Integer, db.ForeignKey('role.id'), primary_key=True)
                         )



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(64), unique=False, nullable=False)
    password_previous = db.Column(db.Text, nullable=True)
    token = db.Column(db.String(64), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship('Role', secondary=userxrole)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(30), default=None)
    birthdate = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return 'User %r' % self.email


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    humanreadablename = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return 'Role %r' % self.name

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    date_of_spent = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sum = db.Column(db.Float, nullable=False, default=0.0)
    comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return 'Employee %r' % self.id

class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30), nullable=False)
    income = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text, nullable=True)
    transactions = db.relationship('Transactions', backref='Category', lazy=True)

    def __repr__(self):
        return 'Category %r' % self.name
