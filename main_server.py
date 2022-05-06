import datetime
import os

from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from PIL import Image
from requests import get, post, put, delete

from data import db_session

from data.users import User
from data.publications import Publication
from data.comments import Comment
from data.messages import Message

from data.forms.login import LoginForm
from data.forms.register import RegisterForm, ExtensionForm
from data.forms.post import PublicationForm
from data.forms.text_form import TextForm
from data.forms.search import SearchForm

from data.resources import user_resource, publication_resource, message_resource, comment_resource

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
    api.add_resource(user_resource.UsersSearchResource, '/api/users/<to_find>')
    api.add_resource(user_resource.UsersListResource, '/api/users')

    api.add_resource(user_resource.UsersSubscriptionsResource, '/api/subscribe/<from_for>/<int:users_id>')
    api.add_resource(user_resource.UsersSubscribeResource, '/api/subscribe/<int:users_id>/<int:subscribers_id>')

    api.add_resource(publication_resource.PublicationsResource, '/api/publications/<int:publications_id>')
    api.add_resource(publication_resource.PublicationsSearchResource, '/api/publications/<to_find>')
    api.add_resource(publication_resource.PublicationsListResource, '/api/publications')

    api.add_resource(publication_resource.PublicationsCheerResource, '/api/cheer/<int:users_id>/<int:publications_id>')

    api.add_resource(message_resource.MessagesResource, '/api/messages/<int:message_id>')
    api.add_resource(message_resource.MessagesListResource, '/api/messages')
    api.add_resource(message_resource.MessagesDialogResource, '/api/messages/<int:sender>/<int:receiver>')

    api.add_resource(comment_resource.CommentsResource, '/api/comments/<int:comment_id>')
    api.add_resource(comment_resource.CommentsListResource, '/api/comments')
    api.add_resource(comment_resource.CommentsTreeResource, '/api/comments_tree/<int:publications_id>')
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
    form = ExtensionForm(CombinedMultiDict((request.files, request.form)))
    if request.method == "GET":
        form.surname.data = current_user.surname
        form.name.data = current_user.name
        form.age.data = current_user.age
        form.portrayal.data = current_user.portrayal
        form.speciality.data = current_user.speciality
        form.avatar.data = Image.open(current_user.avatar[1:])
        form.city_from.data = current_user.city_from
    if form.validate_on_submit():
        file_code = secure_filename(f'{current_user.id}.png')
        filepath = f'static/img/avatars/{file_code}'
        if os.path.exists(filepath):
            os.remove(filepath)
        f = form.avatar.data
        logging.info(filepath)
        if f:
            f.save(filepath)
            image_cutter.resize_for_avatar(filepath)
            logging.info('success')
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
        logging.info(filepath)
        if f:
            f.save(filepath)
            logging.info(image_cutter.squarify(filepath))
            logging.info('success')
        req = post(path + '/api/publications',
                   json={'title': form.title.data,
                         'photo': url_for('static',
                                          filename=f'img/publications/{file_code}'),
                         'description': form.description.data,
                         'author': current_user.id}).json()
        logging.info(str(req))
        return redirect('/publications')
    return render_template('post_publication.html', title='Публикация', form=form)


@app.route('/redact_publication/<int:publications_id>', methods=['GET', 'POST'])
@login_required
def publications_redacting(publications_id):
    form = PublicationForm()
    pub_req = get(path + f'/api/publications/{publications_id}').json()
    logging.info(pub_req)
    publication = pub_req['publication']
    if not publication['author'] == current_user.id or current_user.rank in ('administration', 'moderation'):
        redirect('/')
    if request.method == 'GET':
        form.title.data = publication['title']
        form.description.data = publication['description']
    if form.validate_on_submit():
        req = put(path + f'/api/publications/{publications_id}',
                  json={'title': form.title.data,
                        'description': form.description.data}).json()
        logging.info(str(req))
        return redirect(f'/publication/{publications_id}')
    return render_template('publication_redacting.html', title='Публикация', publication=publication, form=form)


@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/<search>', methods=['GET', 'POST'])
def users_list(search=""):
    search_form = SearchForm()
    req = get(path + f'/api/users{"/" + search if search else ""}').json() 
    logging.info(str(req))
    if search_form.validate_on_submit():
        return redirect(f'/users{"/" + search_form.to_find.data if search_form.to_find.data else ""}')
    return render_template("users_list.html", users=req['users'], n=len(req['users']), form=search_form)


@app.route('/user/<int:users_id>', methods=['GET', 'POST'])
def user_page(users_id):
    form = TextForm()
    user_req = get(path + f'/api/users/{users_id}').json()
    pub_req = get(path + f'/api/publications').json()
    if 'publications' in pub_req:
        publications = list(filter(lambda x: x['author'] == users_id, pub_req['publications']))
    else:
        publications = []
    if current_user.is_authenticated:
        mes_req = get(path + f'/api/messages/{current_user.id}/{users_id}').json()
    else:
        mes_req = {'messages': []}
    logging.info(str(user_req))
    logging.info(str(mes_req))
    if current_user.is_authenticated and form.validate_on_submit():
        req = post(path + '/api/messages',
                   json={'text': form.text.data,
                         'sender_id': current_user.id,
                         'receiver_id': users_id}).json()
        logging.info(str(req))
        return redirect(f'/user/{users_id}')
    return render_template("user_page.html", user=user_req['user'], form=form, messages=mes_req['messages'],
                           publications=publications, n=len(publications))


@app.route('/subscribes/<from_for>/<int:users_id>', methods=['GET', 'POST'])
def list_of_subscribers(from_for, users_id):
    subs_req = get(path + f'/api/subscribe/{from_for}/{users_id}').json()
    logging.info(str(subs_req))
    return render_template("subscribes.html", users=subs_req['users'], n=len(subs_req['users']), users_id=users_id)


@app.route('/subscribe_to/<int:users_id>', methods=['GET', 'POST'])
@login_required
def subscribe(users_id):
    user_req = get(path + f'/api/users/{users_id}').json()
    logging.info(user_req)
    user = user_req['user']
    if user['id'] != current_user.id:
        if current_user.id not in user['subscribed']:
            req = put(path + f'/api/subscribe/{users_id}/{current_user.id}').json()
        else:
            req = delete(path + f'/api/subscribe/{users_id}/{current_user.id}').json()
        logging.info(req)
    return redirect(request.referrer)


@app.route('/cheer/<int:publication_id>', methods=['GET', 'POST'])
@login_required
def cheer(publication_id):
    publication_req = get(path + f'/api/publications/{publication_id}').json()
    logging.info(publication_req)
    publication = publication_req['publication']
    if current_user.id not in publication['cheers']:
        req = put(path + f'/api/cheer/{current_user.id}/{publication_id}').json()
    else:
        req = delete(path + f'/api/cheer/{current_user.id}/{publication_id}').json()
    logging.info(req)
    return redirect(request.referrer)


@app.route('/', methods=['GET', 'POST'])
@app.route('/publications', methods=['GET', 'POST'])
@app.route('/publications/<search>', methods=['GET', 'POST'])
def publications_list(search=""):
    search_form = SearchForm()
    pub_req = get(path + f'/api/publications{"/" + search if search else ""}').json()
    user_req = get(path + '/api/users').json()
    logging.info(str(pub_req))
    if search_form.validate_on_submit():
        return redirect(f'/publications{"/" + search_form.to_find.data if search_form.to_find.data else ""}')
    return render_template("publications_list.html", publications=pub_req['publications'], users=user_req['users'],
                           n=len(pub_req['publications']), form=search_form)


@app.route('/reported_publications', methods=['GET', 'POST'])
@app.route('/reported_publications/<search>', methods=['GET', 'POST'])
def reported_publications_list(search=""):
    if current_user.rank not in ['moderation', 'administration']:
        redirect('/')
    search_form = SearchForm()
    pub_req = get(path + f'/api/publications{"/" + search if search else ""}').json()
    user_req = get(path + '/api/users').json()
    logging.info(str(pub_req))
    if search_form.validate_on_submit():
        return redirect(f'/reported_publications{"/" + search_form.to_find.data if search_form.to_find.data else ""}')
    publications = list(filter(lambda x: x['reported'], pub_req['publications']))
    return render_template("publications_list.html", publications=publications, users=user_req['users'],
                           n=len(publications), form=search_form)


@app.route('/publication/<int:publication_id>', methods=['GET', 'POST'])
def show_publication(publication_id):
    form = TextForm()
    pub_req = get(path + f'/api/publications/{publication_id}').json()
    com_req = get(path + f'/api/comments_tree/{publication_id}').json()
    logging.info(str(pub_req))
    if current_user.is_authenticated and form.validate_on_submit():
        req = post(path + '/api/comments',
                   json={'text': form.text.data,
                         'sender': current_user.id,
                         'receiver': publication_id}).json()
        logging.info(str(req))
        return redirect(f'/publication/{publication_id}')
    return render_template("publication.html", publication=pub_req['publication'],
                           form=form, comments=com_req['comments'])


@app.route('/deport_publication/<int:publications_id>', methods=['GET', 'POST'])
@login_required
def deport_publication(publications_id):
    pub_req = get(path + f'/api/publications/{publications_id}').json()
    logging.info(pub_req)
    publication = pub_req['publication']
    if publication["reported"] and current_user.rank in ['moderation', 'administration']:
        req = put(path + f'/api/publications/{publications_id}', json={'reported': False, }).json()
        logging.info(req)
    return redirect(request.referrer)


@app.route('/report_publication/<int:publications_id>', methods=['GET', 'POST'])
@login_required
def report_publication(publications_id):
    pub_req = get(path + f'/api/publications/{publications_id}').json()
    logging.info(pub_req)
    publication = pub_req['publication']
    if publication['author'] != current_user.id and not publication["reported"]:
        req = put(path + f'/api/publications/{publications_id}', json={'reported': True, }).json()
        logging.info(req)
    return redirect(request.referrer)


@app.route('/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    message = get(path + f'/api/messages/{message_id}').json()['message']
    if current_user.id == message['sender']:
        req = delete(path + f'/api/messages/{message_id}').json()
        logging.info(str(req))
    return redirect(request.referrer)


@app.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = get(path + f'/api/comments/{comment_id}').json()['comment']
    if current_user.id == comment['sender']:
        req = delete(path + f'/api/comments/{comment_id}').json()
        logging.info(str(req))
    return redirect(request.referrer)


@app.route('/delete_publication/<int:publications_id>')
@login_required
def delete_publication(publications_id):
    publication = get(path + f'/api/publications/{publications_id}').json()['publication']
    if publication['author'] == current_user.id or current_user.rank in ('administration', 'moderation'):
        file_code = secure_filename(f'{str(publications_id) + "-" + str(publication["author"])}.png')
        filepath = f'static/img/publications/{file_code}'
        if os.path.exists(filepath):
            os.remove(filepath)
        req = delete(path + f'/api/publications/{publications_id}').json()
        logging.info(str(req))
    return redirect(request.referrer)


if __name__ == '__main__':
    main()
