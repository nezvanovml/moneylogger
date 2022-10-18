import datetime

from app import app, config, mail, db, User, Role, userxrole, \
    Transactions, ALLOWED_EXTENSIONS, Categories
from flask import request, render_template, redirect, Response, url_for, flash
from functools import wraps

import hashlib
import random
import json
import csv
import os
import uuid
import re
from flask_mail import Message
from utils import allowed_file, check_password_was_not_used_earlier, check_list1_is_in_list2
from sqlalchemy.sql import select, update, insert, delete

def add_user(email, password, first_name, last_name, birthdate, active=True):
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email, password=hashlib.sha256(password.encode('utf-8')).hexdigest(),
                    first_name=first_name, last_name=last_name, active=active, birthdate=birthdate)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False
        else:
            return user.id
    return user.id

def add_role(name, humanreadablename=""):
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, humanreadablename=humanreadablename)
        try:
            db.session.add(role)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False
        else:
            return role.id
    return role.id

def add_role_for_user(user_id, role_id):
    user = User.query.filter(User.id == user_id).first()
    role = Role.query.filter(Role.id == role_id).first()
    if user and role:
        conn = db.engine.connect()
        result = conn.execute(
            select(userxrole).where(userxrole.c.user == user.id,
                                        userxrole.c.role == role.id))
        if not result.fetchone():
            conn.execute(userxrole.insert().values(user=user.id, role=role.id))
            return True
        else:
            return False
    else:
        return False

def remove_role_for_user(user_id, role_id):
    user = User.query.filter(User.id == user_id).first()
    role = Role.query.filter(Role.id == role_id).first()
    if user and role:
        conn = db.engine.connect()
        result = conn.execute(
            select(userxrole).where(userxrole.c.user == user.id,
                                        userxrole.c.role == role.id))
        if result.fetchone():
            conn.execute(
                delete(userxrole).where(userxrole.c.user == user.id,
                                            userxrole.c.role == role.id))
            return True
        else:
            return False
    else:
        return False

def change_password(user_id, password):
    user = User.query.filter(User.id == user_id).first()
    if user and len(password) > 0:
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'  # от 8 символов в разном регистре с цифрами
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if re.match(pattern, password) is None:
            return False
        elif check_password_was_not_used_earlier(hashed_password, user.password_previous):
            return False
        user.password = hashed_password
        if not user.password_previous:
            user.password_previous = hashed_password
        else:
            user.password_previous = f"{user.password_previous};{hashed_password}"
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return False
        else:
            return True
    return False

def have_roles(needed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', None)
            if token:
                actual_roles = []
                roles = Role.query \
                    .join(userxrole, userxrole.columns.role == Role.id) \
                    .join(User, User.id == userxrole.columns.employee) \
                    .filter(User.token == token, User.active == 't') \
                    .all()
                for role in roles:
                    actual_roles.append(role.name)
                if check_list1_is_in_list2(needed_roles, actual_roles):
                    return fn(*args, **kwargs)
                else:
                    return Response('NOT ENOUGH PRIVILEGIES', status=401)
            return Response('UNAUTHORIZED', status=401)

        return decorated_function

    return wrapper

def get_current_user():
    token = request.headers.get('Authorization', None)
    if token:
        user = User.query.filter(User.token == token).first()
        if user:
            return user.id
    return None

def is_authorized():
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            if get_current_user():
                return fn(*args, **kwargs)
            return Response('UNAUTHORIZED', status=401)

        return decorated_function

    return wrapper

# Create a user to test with
@app.route("/createadmin",methods=['GET'])
def create_admin():
    role = add_role("SUPERUSER","SUPERUSER ROLE")
    user = add_user(email='admin@localhost', password="admin", first_name='SUPER',last_name='ADMIN', birthdate=datetime.datetime.utcnow())
    if role and user:
        add_role_for_user(user, role)
    return Response("OK.", mimetype="text/html",
                        status=200)


@app.route('/transactions', methods=['GET', 'POST', 'PUT', 'DELETE'])
@is_authorized()
def transactions():
    if request.method == 'GET':
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)

        if start_date:
            try:
                start_date = datetime.datetime.strptime(start_date, '%d.%m.%Y').date()
            except ValueError:
                return Response("Incorrect format of start_date.", mimetype="text/html", status=400)

        if end_date:
            try:
                end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y').date()
            except ValueError:
                return Response("Incorrect format of end_date.", mimetype="text/html", status=400)

        if not end_date and not start_date:
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user()).order_by(Transactions.date_of_spent).all()
            result = {'count': len(transactions),'transactions': []}
            for transaction in transactions:
                result['transactions'].append({
                    'id': transaction.id,
                    'category': transaction.category_id,
                    'date': transaction.date_of_spent.strftime("%d.%m.%Y"),
                    'sum': transaction.sum,
                    'comment': transaction.comment
                })
            return Response(json.dumps(result), mimetype="application/json", status=200)
        elif end_date and not start_date:
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user(), Transactions.date_of_spent < end_date).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions),'transactions': []}
            for transaction in transactions:
                result['transactions'].append({
                    'id': transaction.id,
                    'category': transaction.category_id,
                    'date': transaction.date_of_spent.strftime("%d.%m.%Y"),
                    'sum': transaction.sum,
                    'comment': transaction.comment
                })
            return Response(json.dumps(result), mimetype="application/json", status=200)
        elif start_date and not end_date:
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user(), Transactions.date_of_spent >= start_date).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions),'transactions': []}
            for transaction in transactions:
                result['transactions'].append({
                    'id': transaction.id,
                    'category': transaction.category_id,
                    'date': transaction.date_of_spent.strftime("%d.%m.%Y"),
                    'sum': transaction.sum,
                    'comment': transaction.comment
                })
            return Response(json.dumps(result), mimetype="application/json", status=200)
        else:
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user(), Transactions.date_of_spent >= start_date, Transactions.date_of_spent < end_date).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions),'transactions': []}
            for transaction in transactions:
                result['transactions'].append({
                    'id': transaction.id,
                    'category': transaction.category_id,
                    'date': transaction.date_of_spent.strftime("%d.%m.%Y"),
                    'sum': transaction.sum,
                    'comment': transaction.comment
                })
            return Response(json.dumps(result), mimetype="application/json", status=200)
    else:
        return Response("OK.", mimetype="text/html", status=200)

@app.route('/import/csv', methods=['POST'])
@is_authorized()
def load_from_csv_monefy():
    if 'file' not in request.files:
        return Response(f"Provide file sent in form, where key=file", mimetype="text/html", status=400)
    file = request.files['file']
    if file.filename != '':
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = uuid.uuid4().hex
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                required_fields = ['date', 'category', 'amount', 'description']
                for field in required_fields:
                    if field not in reader.fieldnames:
                        return Response(f"Error adding data from file. It seems, that file have no required columns.",
                                        mimetype="text/html",
                                        status=400)
                user_id = get_current_user()
                for row in reader:
                    category = Categories.query.filter(Categories.name == row['category'],
                                                       Categories.user_id == user_id).first()
                    if not category:
                        category = Categories(user_id=user_id, name=row['category'])
                        try:
                            db.session.add(category)
                            db.session.commit()
                        except Exception as error:
                            db.session.rollback()
                            return Response(f"Error adding data from file. Check file format. Description: {error}",
                                            mimetype="text/html",
                                            status=400)
                    try:
                        date = datetime.datetime.strptime(row['date'], '%d.%m.%Y').date()
                    except ValueError:
                        date = datetime.datetime.utcnow()

                    try:
                        sum = float(row['amount'])
                    except ValueError:
                        sum = 0.0

                    transaction = Transactions(user_id=user_id,
                                               category_id=category.id,
                                               date_of_spent=date,
                                               sum=sum,
                                               comment=row['description'])
                    try:
                        db.session.add(transaction)
                        db.session.commit()
                    except Exception as error:
                        db.session.rollback()
                        return Response(f"Error adding data from file. Check file format. Description: {error}",
                                        mimetype="text/html",
                                        status=400)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return Response("OK", mimetype="text/html", status=200)
    return Response(f"Empty file provided.", mimetype="text/html", status=400)


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password', " ")
    if len(password) > 0:
        user = User.query.filter(User.password == hashlib.sha256(password.encode('utf-8')).hexdigest(),
                                 User.email == email).first()
        if user:
            if not user.token or len(user.token) != 64:
                user.token = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                db.session.commit()
            return Response(json.dumps({'status': 'SUCCESS', 'token': user.token}), mimetype="application/json", status=200)
    return Response(json.dumps({'status': 'ERROR', 'description': 'check provided credentials.'}),
                        mimetype="application/json", status=404)

@app.route('/logout', methods=['POST'])
@is_authorized()
def logout():
    token = request.headers.get('Authorization', None)
    if token:
        user = User.query.filter(User.token == token).first()
        if user:
            user.token = None
            db.session.commit()
            return Response(json.dumps({'status': 'SUCCESS', 'description': 'token destroyed.'}),
                            mimetype="application/json", status=200)
    return Response(json.dumps({'status': 'ERROR', 'description': 'check provided credentials.'}),
                    mimetype="application/json", status=404)


if __name__ == "__main__":
    app.run(debug=False)
