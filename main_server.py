import datetime
import os

from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.utils import secure_filename
from requests import get, post, put, delete

from data import db_session

from data.users import User
from data.publications import Publication
from data.comments import Comment
from data.messages import Message

from data.forms.login import LoginForm
from data.forms.register import RegisterForm, ExtensionForm
from data.forms.post import PublicationForm

from data.resources import user_resource, publication_resource

import logging
import image_cutter

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
path = 'http://localhost:8080'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/paintogram.db")
    api.add_resource(user_resource.UsersResource, '/api/users/<int:users_id>')
    api.add_resource(user_resource.UsersListResource, '/api/users')
    api.add_resource(publication_resource.PublicationsResource, '/api/publications/<int:publications_id>')
    api.add_resource(publication_resource.PublicationsListResource, '/api/publications')
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


@login_required
@app.route('/logout')
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


@app.route('/extension', methods=['GET', 'POST'])
@login_required
def extension():
    form = ExtensionForm()
    if form.validate_on_submit():
        file_code = secure_filename(f'{current_user.id}.png')
        filepath = f'static/img/avatars/{file_code}'
        if os.path.exists(filepath):
            os.remove(filepath)
        f = form.avatar.data
        if f:
            f.save(filepath)
            image_cutter.resize_for_avatar(filepath)
        req = put(path + '/api/users' + f'/{current_user.id}',
                  json={'surname': form.surname.data,
                        'age': form.age.data,
                        'portrayal': form.portrayal.data,
                        'speciality': form.speciality.data,
                        'city_from': form.city_from.data,
                        'avatar': url_for('static', filename=(f'img/avatars/{file_code}'
                                                              if f else 'img/avatars/default.png'))}).json()
        logging.info(str(req))
        return redirect('/')
    return render_template('extension.html', title='Дополнение', form=form)


@app.route('/users', methods=['GET', 'POST'])
def users_list(search=""):
    req = get(path + '/api/users').json()
    logging.info(str(req))
    return render_template("users_list.html", users=req['users'], n=len(req['users']))


# @app.route('/users/<int:users_id>', methods=['GET', 'POST'])
# def user_page(users_id, search=""):
#     req = get(path + f'/api/users/<int:users_id>').json()
#     logging.info(str(req))
#     return render_template("user_page.html", users=req['users'], n=len(req['users']))


@app.route('/post_publication', methods=['GET', 'POST'])
@login_required
def publications_posting():
    form = PublicationForm()
    if form.validate_on_submit():
        logging.info(str(get(path + '/api/publications').json()))
        publication_id = max([publication['id'] for publication
                              in get(path + '/api/publications').json()['publications']] + [0]) + 1
        file_code = secure_filename(f'{str(publication_id) + "-" + str(current_user.id)}.png')
        filepath = f'static/img/publications/{file_code}'
        if os.path.exists(filepath):
            os.remove(filepath)
        f = form.photo.data
        if f:
            f.save(filepath)
            logging.info(image_cutter.squarify(filepath))
        req = post(path + '/api/publications',
                   json={'title': form.title.data,
                         'photo': url_for('static',
                                          filename=f'img/publications/{file_code}'),
                         'description': form.description.data,
                         'author': current_user.id}).json()
        logging.info(str(req))
        return redirect('/publications')
    return render_template('post_publication.html', title='Публикация', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/publications', methods=['GET', 'POST'])
def publications_list(search=""):
    pub_req = get(path + '/api/publications').json()
    user_req = get(path + '/api/users').json()
    logging.info(str(pub_req))
    return render_template("publications_list.html", publications=pub_req['publications'], users=user_req['users'],
                           n=len(pub_req['publications']))


@app.route('/delete_publication/<int:publications_id>')
@login_required
def delete_publication(publications_id):
    publication = get(path + f'/api/publications/{publications_id}').json()['publication']
    if publication['author'] == current_user.id:
        file_code = secure_filename(f'{str(publications_id) + "-" + str(publication["author"])}.png')
        filepath = f'static/img/publications/{file_code}'
        if os.path.exists(filepath):
            os.remove(filepath)
        req = delete(path + f'/api/publications/{publications_id}').json()
        logging.info(str(req))
    return redirect(request.referrer)


if __name__ == '__main__':
    main()
