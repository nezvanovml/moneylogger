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
                    return Response(json.dumps(
                        {'status': 'UNAUTHORIZED', 'description': f"You have no permissions to perform request."}),
                                    mimetype="application/json",
                                    status=401)
            return Response(json.dumps(
                {'status': 'UNAUTHORIZED', 'description': f"You must authenticate first to perform request."}),
                            mimetype="application/json",
                            status=401)

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
            return Response(json.dumps({'status': 'UNAUTHORIZED', 'description': f"You must authenticate first to perform request."}),
                            mimetype="application/json",
                            status=401)

        return decorated_function

    return wrapper


# Create a user to test with
@app.route("/init", methods=['GET'])
def initialization():
    admin_role = add_role("SUPERUSER", "SUPERUSER ROLE")
    user_role = add_role("USER", "Standard user")
    user = add_user(email='admin@localhost', password="admin", first_name='SUPER', last_name='ADMIN',
                    birthdate=datetime.datetime.utcnow())
    if admin_role and user:
        add_role_for_user(user, admin_role)
    if user_role and user:
        add_role_for_user(user, user_role)
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
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user()).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions), 'transactions': []}
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
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user(),
                                                     Transactions.date_of_spent < end_date).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions), 'transactions': []}
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
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user(),
                                                     Transactions.date_of_spent >= start_date).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions), 'transactions': []}
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
            transactions = Transactions.query.filter(Transactions.user_id == get_current_user(),
                                                     Transactions.date_of_spent >= start_date,
                                                     Transactions.date_of_spent < end_date).order_by(
                Transactions.date_of_spent).all()
            result = {'count': len(transactions), 'transactions': []}
            for transaction in transactions:
                result['transactions'].append({
                    'id': transaction.id,
                    'category': transaction.category_id,
                    'date': transaction.date_of_spent.strftime("%d.%m.%Y"),
                    'sum': transaction.sum,
                    'comment': transaction.comment
                })
            return Response(json.dumps(result), mimetype="application/json", status=200)
    elif request.method == 'PUT':

        user_id = get_current_user()

        category_id = request.args.get('category', None)
        try:
            category_id = int(category_id)
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Category is not a int."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Category not provided."}),
                            mimetype="application/json",
                            status=400)
        category = Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).first()
        if not category:
            return Response(
                json.dumps({'status': 'ERROR', 'description': f"Category not found."}),
                mimetype="application/json",
                status=404)

        date = request.args.get('date', None)
        try:
            date = datetime.datetime.strptime(date, '%d.%m.%Y').date()
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Incorrect format of date."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Date not provided."}),
                            mimetype="application/json",
                            status=400)

        sum = request.args.get('sum', None)
        try:
            sum = float(sum)
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Sum is not a int/float."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Sum not provided."}),
                            mimetype="application/json",
                            status=400)

        comment = request.args.get('comment', None)
        transaction = Transactions(user_id=user_id,
                                   category_id=category.id,
                                   date_of_spent=date,
                                   sum=sum,
                                   comment=comment)
        try:
            db.session.add(transaction)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return Response(json.dumps({'status': 'ERROR', 'description': error}), mimetype="application/json",
                            status=500)
        return Response(json.dumps({'status': 'SUCCESS', 'description': 'ADDED', 'id': transaction.id}), mimetype="application/json",
                        status=201)
    elif request.method == 'POST':

        user_id = get_current_user()

        transaction_id = request.args.get('transaction', None)
        try:
            transaction_id = int(transaction_id)
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Transaction is not a int."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Transaction not provided."}),
                            mimetype="application/json",
                            status=400)
        transaction = Transactions.query.filter(Transactions.id == transaction_id, Transactions.user_id == user_id).first()
        if not transaction:
            return Response(
                json.dumps({'status': 'ERROR', 'description': f"Transaction not found."}),
                mimetype="application/json",
                status=404)

        category_id = request.args.get('category', None)
        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                return Response(json.dumps({'status': 'ERROR', 'description': f"Category is not a int."}),
                                mimetype="application/json",
                                status=400)
            category = Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).first()
            if not category:
                return Response(
                    json.dumps({'status': 'ERROR', 'description': f"Category not found."}),
                    mimetype="application/json",
                    status=404)
            transaction.category_id = category_id

        date = request.args.get('date', None)
        if date:
            try:
                date = datetime.datetime.strptime(date, '%d.%m.%Y').date()
            except ValueError:
                return Response(json.dumps({'status': 'ERROR', 'description': f"Incorrect format of date."}),
                                mimetype="application/json",
                                status=400)
            transaction.date_of_spent = date

        sum = request.args.get('sum', None)
        if sum:
            try:
                sum = float(sum)
            except ValueError:
                return Response(json.dumps({'status': 'ERROR', 'description': f"Sum is not a int/float."}),
                                mimetype="application/json",
                                status=400)
            transaction.sum = sum

        comment = request.args.get('comment', None)
        if comment:
            transaction.comment = str(comment)

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return Response(json.dumps({'status': 'ERROR', 'description': error}), mimetype="application/json",
                            status=500)
        return Response(json.dumps({'status': 'SUCCESS', 'description': 'UPDATED', 'id': transaction.id}), mimetype="application/json",
                        status=201)
    elif request.method == 'DELETE':

        user_id = get_current_user()

        transaction_id = request.args.get('transaction', None)
        try:
            transaction_id = int(transaction_id)
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Transaction is not a int."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Transaction not provided."}),
                            mimetype="application/json",
                            status=400)
        transaction = Transactions.query.filter(Transactions.id == transaction_id,
                                                Transactions.user_id == user_id).first()
        if not transaction:
            return Response(
                json.dumps({'status': 'ERROR', 'description': f"Transaction not found."}),
                mimetype="application/json",
                status=404)

        Transactions.query.filter(Transactions.id == transaction_id,
                                  Transactions.user_id == user_id).delete()
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return Response(json.dumps({'status': 'ERROR', 'description': error}), mimetype="application/json",
                            status=500)
        return Response(json.dumps({'status': 'SUCCESS', 'description': 'DELETED'}), mimetype="application/json",
                        status=201)
    else:
        return Response(json.dumps({'status': 'ERROR', 'description': 'Method not allowed.'}), mimetype="application/json", status=405)

@app.route('/categories', methods=['GET', 'POST', 'PUT', 'DELETE'])
@is_authorized()
def categories():
    if request.method == 'GET':
        categories = Categories.query.filter(Categories.user_id == get_current_user()).all()
        result = {'count': len(categories), 'categories': []}
        for category in categories:
            result['categories'].append({
                'id': category.id,
                'name': category.name,
                'income': category.income,
                'description': category.description
            })
        return Response(json.dumps(result), mimetype="application/json", status=200)
    elif request.method == 'PUT':

        user_id = get_current_user()
        name = request.args.get('name', None)
        if not name:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Name not provided."}),
                            mimetype="application/json",
                            status=400)

        income = request.args.get('income', None)
        if not income:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Income not provided."}),
                            mimetype="application/json",
                            status=400)
        income = True if income == 'True' else False

        description = request.args.get('description', None)

        category = Categories(user_id=user_id,
                                   name=name,
                                   income=income,
                                   description=description)
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return Response(json.dumps({'status': 'ERROR', 'description': error}), mimetype="application/json",
                            status=500)
        return Response(json.dumps({'status': 'SUCCESS', 'description': 'ADDED', 'id': category.id}), mimetype="application/json",
                        status=201)
    elif request.method == 'POST':

        user_id = get_current_user()

        category_id = request.args.get('category', None)
        try:
            category_id = int(category_id)
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Category is not a int."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Category not provided."}),
                            mimetype="application/json",
                            status=400)

        category = Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).first()
        if not category:
            return Response(
                json.dumps({'status': 'ERROR', 'description': f"Category not found."}),
                mimetype="application/json",
                status=404)

        name = request.args.get('name', None)
        if name:
            category.name = name

        income = request.args.get('income', None)
        if income:
            income = True if income == 'True' else False
            category.income = income

        description = request.args.get('description', None)
        if description:
            category.description = str(description)

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return Response(json.dumps({'status': 'ERROR', 'description': error}), mimetype="application/json",
                            status=500)
        return Response(json.dumps({'status': 'SUCCESS', 'description': 'UPDATED', 'id': category.id}), mimetype="application/json",
                        status=201)
    elif request.method == 'DELETE':

        user_id = get_current_user()

        category_id = request.args.get('category', None)
        try:
            category_id = int(category_id)
        except ValueError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Category is not a int."}),
                            mimetype="application/json",
                            status=400)
        except TypeError:
            return Response(json.dumps({'status': 'ERROR', 'description': f"Category not provided."}),
                            mimetype="application/json",
                            status=400)
        category = Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).first()
        if not category:
            return Response(
                json.dumps({'status': 'ERROR', 'description': f"Category not found."}),
                mimetype="application/json",
                status=404)

        Categories.query.filter(Categories.id == category_id, Categories.user_id == user_id).delete()
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return Response(json.dumps({'status': 'ERROR', 'description': error}), mimetype="application/json",
                            status=500)
        return Response(json.dumps({'status': 'SUCCESS', 'description': 'DELETED'}), mimetype="application/json",
                        status=201)
    else:
        return Response(json.dumps({'status': 'ERROR', 'description': 'Method not allowed.'}), mimetype="application/json", status=405)

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
    if not request.is_json:
        return Response(json.dumps({'status': 'ERROR', 'description': 'Provide correct JSON structure.'}),
                        mimetype="application/json", status=400)
    data = request.get_json()
    if data:
        email = data.get('email')
        password = data.get('password', " ")
        if len(password) > 0:
            user = User.query.filter(User.password == hashlib.sha256(password.encode('utf-8')).hexdigest(),
                                     User.email == email).first()
            if user:
                if not user.token or len(user.token) != 64:
                    user.token = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                    db.session.commit()
                return Response(json.dumps({'status': 'SUCCESS', 'token': user.token}), mimetype="application/json",
                                status=200)
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

@app.route('/checkauth', methods=['GET'])
@is_authorized()
def checkauth():
    return Response(json.dumps({'status': 'SUCCESS', 'description': 'Token is correct.'}),
                            mimetype="application/json", status=200)



if __name__ == "__main__":
    app.run(debug=False)
