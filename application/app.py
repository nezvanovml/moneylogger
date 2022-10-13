import os
import yaml
import pathlib
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security
from flask_mail import Mail
from flask_babelex import Babel
from flask_admin import Admin
from admin import DashboardView, UsersView, TransactionsView, RolesView, CategoriesView


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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', None)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["postgres"]["user"]}:{os.environ.get("POSTGRES_PASSWORD", "")}@{config["postgres"]["host"]}:{config["postgres"]["port"]}/{config["postgres"]["database"]}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', None)
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'email'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)

@babel.localeselector
def get_locale():
        return 'ru'

app.config['MAIL_SERVER'] = config["email"]["host"]
app.config['MAIL_PORT'] = config["email"]["port"]
app.config['MAIL_USE_SSL'] = config["email"]["use_ssl"]
app.config['MAIL_USERNAME'] = config["email"]["login"]
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD", "")
mail = Mail(app)

# Define models
rolexuser = db.Table('rolexuser',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return 'Role %r' % self.name

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    patronymic = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(30), nullable=True)
    birthdate = db.Column(db.DateTime, nullable=True)
    password = db.Column(db.String(255))
    token = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=rolexuser,
                            backref=db.backref('users', lazy='dynamic'))
    transactions = db.relationship('Transactions', backref='User',lazy=True)
    categories = db.relationship('Categories', backref='User', lazy=True)

    def __repr__(self):
        return 'User %r' % self.email

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    date_of_spent = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sum = db.Column(db.Float, nullable=False, default=0.0)
    comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return 'Employee %r' % self.login

class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30), nullable=False)
    comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return 'Category %r' % self.login

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = Admin(app, name='MoneyLogger', template_mode='bootstrap3',index_view=DashboardView())
admin.add_view(UsersView(User, db.session, name='Пользователи'))
admin.add_view(RolesView(Role, db.session, name='Роли'))
admin.add_view(TransactionsView(Transactions, db.session, name='Транзакции'))
admin.add_view(CategoriesView(Categories, db.session, name='Категории'))
