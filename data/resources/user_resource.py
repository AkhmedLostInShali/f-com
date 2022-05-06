from flask import jsonify, request
from flask_restful import abort, Resource
from .. import db_session, my_parsers
from ..users import User
import logging

logging.basicConfig(level=logging.INFO)

parser = my_parsers.UserParser()


def abort_if_user_not_found(users_id):
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")


class UsersResource(Resource):
    def get(self, users_id):
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        user_dict = user.to_dict(only=('id', 'nickname', 'surname', 'name', 'age', 'rank', 'avatar', 'portrayal',
                                       'city_from', 'speciality', 'email', 'hashed_password'))
        user_dict['subscribed'] = [u.id for u in user.subscribed]
        user_dict['subscribes'] = [u.id for u in user.subscribes]
        return jsonify({'user': user_dict})

    def delete(self, users_id):
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        if users_id < 3:
            return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, users_id):
        abort_if_user_not_found(users_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(User).all()]:
            return jsonify({'error': 'Id already exists'})
        if request.json.get('email') and request.json.get('email') in [user.email for user
                                                                       in db_sess.query(User).all()]:
            return jsonify({'error': 'email already exists'})
        user = db_sess.query(User).get(users_id)
        user.id = request.json['id'] if request.json.get('id') else user.id
        user.email = request.json['email'] if request.json.get('email') else user.email
        user.nickname = request.json['nickname'] if request.json.get('nickname') else user.nickname
        user.surname = request.json['surname'] if request.json.get('surname') else user.surname
        user.name = request.json['name'] if request.json.get('name') else user.name
        user.age = request.json['age'] if request.json.get('age') else user.age
        user.portrayal = request.json['portrayal'] if request.json.get('portrayal') else user.portrayal
        user.speciality = request.json['speciality'] if request.json.get('speciality') else user.speciality
        user.avatar = request.json['avatar'] if request.json.get('avatar') else user.avatar
        user.city_from = request.json['city_from'] if request.json.get('city_from') else user.city_from
        user.rank = request.json['rank'] if request.json.get('rank') else user.rank
        if request.json.get('password') and request.json.get('password_again'):
            if request.json['password'] != request.json['password_again']:
                return jsonify({'error': "Passwords doesn't match"})
            user.set_password(request.json.get('password'))
        elif request.json.get('password') or request.json.get('password_again'):
            return jsonify({'error': "Requires both of 'password' and 'password again' or none of them"})
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify({'users': [user.to_dict(only=('id', 'nickname', 'surname', 'name', 'rank', 'avatar',
                                                     'speciality'))
                                  for user in users]})

    def post(self):
        args = parser.parse_args()
        if request.json['password'] != request.json['password_again']:
            return jsonify({'error': "Passwords doesn't match"})
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(User).all()]:
            return jsonify({'error': 'Id already exists'})
        if request.json.get('email') in [user.email for user in db_sess.query(User).all()]:
            return jsonify({'error': 'Email already exists'})

        user = User()
        if args.get('id'):
            user.id = args.get('id')
        user.email = args['email']
        # user.surname = args['surname']
        user.nickname = args['nickname']
        user.name = args['name']
        user.avatar = args['avatar']
        # user.age = args['age']
        # user.position = args['position']
        # user.speciality = args['speciality']
        # user.address = args['address']
        # user.city_from = args['city_from']
        user.set_password(args['password'])

        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersSearchResource(Resource):
    def get(self, to_find):
        db_sess = db_session.create_session()
        search_like = f"%{'%'.join(to_find.split())}%"
        users = db_sess.query(User).filter(User.nickname.like(search_like) | User.name.like(search_like) |
                                           User.surname.like(search_like)).all()
        return jsonify({'users': [user.to_dict(only=('id', 'nickname', 'surname', 'name', 'rank', 'avatar'))
                                  for user in users]})


class UsersSubscriptionsResource(Resource):
    def get(self, from_for, users_id):
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        if from_for == 'for':
            subscriptions = [sub.id for sub in user.subscribed]
        else:
            subscriptions = [sub.id for sub in user.subscribes]
        logging.info(subscriptions)
        users = db_sess.query(User).filter(User.id.in_(subscriptions)).all()
        return jsonify({'users': [user.to_dict(only=('id', 'nickname', 'surname', 'name', 'rank', 'avatar'))
                                  for user in users]})


class UsersSubscribeResource(Resource):
    def put(self, users_id, subscribers_id):
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        subscriber = db_sess.query(User).get(subscribers_id)
        user.subscribed.append(subscriber)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def delete(self, users_id, subscribers_id):
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        subscriber = db_sess.query(User).get(subscribers_id)
        user.subscribed.remove(subscriber)
        db_sess.commit()
        return jsonify({'success': 'OK'})
