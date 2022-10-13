from app import app, config, mail, user_datastore, db, User, Role, Transactions
from flask_security.utils import hash_password
from flask import Flask, request, render_template, redirect, Response, url_for, flash
from sqlalchemy.orm.exc import NoResultFound
import json
import hashlib
from flask_mail import Message
from utils import verify_password
from flask_security import logout_user
from flask_login import login_user

# Create a user to test with
@app.route("/initusers",methods=['GET'])
def create_admin():
    user_datastore.find_or_create_role('admin', description='Full-admin access')
    if not User.query.filter(User.email=='admin@admin.admin').first():
        user_datastore.create_user(email='admin@admin.admin', password=hash_password('admin'), name='admin', surname='full')
        user_datastore.add_role_to_user(user='admin@admin.admin', role='admin')
        db.session.commit()
        return Response("ADMIN: superuser (admin@admin.admin) with password=admin successfully created.", mimetype="text/html",
                        status=200)
    else:
        return Response("ADMIN: superuser (admin) already created.", mimetype="text/html", status=200)

@app.route('/auth', methods=['POST']) # define login page path
def auth(): # define login page fucntion
    login = request.form.get('login')
    password = request.form.get('password')
    print(f'AUTH:{login}/{password}')
    try:
        user = db.session.query(User).where(User.email == login).one()
    except NoResultFound:
        flash('Ошибка авторизации. Проверьте корректность введённых логина/пароля и наличие прав доступа к панели управления.')
        return redirect(url_for('mainpage'))  # if the user doesn't exist or password is wrong, reload the page
    if not verify_password(password, user.password):
        flash('Ошибка авторизации. Проверьте корректность введённых логина/пароля и наличие прав доступа к панели управления.')
        return redirect(url_for('mainpage'))  # if the user doesn't exist or password is wrong, reload the page

    login_user(user)
    flash('Успешная авторизация.')
    return redirect('/admin')

@app.route('/logoutpage')
def logout():
    logout_user()
    return redirect('/admin')

@app.route("/authpage", methods=['GET'])
def mainpage():
    return render_template('login.html')

@app.route('/', methods=['GET'])
def test():
    msg = Message(body="Hello", sender=(config["email"]["sender_name"], config["email"]["login"]), subject="Hello from MoneyLogger")
    msg.add_recipient("nezvanovml@mail.ru")
    mail.send(msg)
    return Response("OK", mimetype="text/html", status=200)



if __name__ == "__main__":
    app.run(debug=False)







