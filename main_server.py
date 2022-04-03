from flask import Flask, redirect, url_for, render_template, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from requests import get, post

from data import db_session

from data.users import User
from data.publications import Publication
from data.comments import Comment
from data.messages import Message

from data.forms.login import LoginForm
from data.forms.register import RegisterForm, ExtensionForm

from data.resources import user_resource

import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
path = 'http://localhost:8080'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/paintogram.db")
    api.add_resource(user_resource.UsersResource, '/api/v2/users/<int:users_id>')
    api.add_resource(user_resource.UsersListResource, '/api/users')
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        req = post(path + '/api/users',
                   json={'email': form.email.data,
                         'password': form.password.data,
                         'password_again': form.password_again.data,
                         'name': form.name.data,
                         'nickname': form.nickname.data,
                         'avatar': url_for('static', filename='img/avatars/default.png')}).json()
        logging.info(str(req))
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/users', methods=['GET', 'POST'])
def users_list(search=""):
    req = get(path + '/api/users').json()
    logging.info(str(req))
    return render_template("users_list.html", users=req['users'], n=len(req['users']))


if __name__ == '__main__':
    main()