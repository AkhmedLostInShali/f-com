from flask import url_for
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


subscribes = sqlalchemy.Table('subscribes', SqlAlchemyBase.metadata,
                              sqlalchemy.Column('subscriber_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'),
                                                index=True),
                              sqlalchemy.Column('subscribed_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'),
                                                index=True))


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    portrayal = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    city_from = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    rank = sqlalchemy.Column(sqlalchemy.String, default='observer')
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    subscribed = orm.relation('User', secondary=subscribes,
                              primaryjoin=(subscribes.c.subscriber_id == id),
                              secondaryjoin=(subscribes.c.subscribed_id == id),
                              backref='subscribes',
                              lazy='dynamic')

    def to_subscribe(self, user):
        if not self.is_friended(user):
            self.subscribed.append(user)
            return self

    def to_unsubscribe(self, user):
        if self.is_friended(user):
            self.subscribed.remove(user)
            return self

    def is_subscriber(self, user):
        return self.subscribed.filter_by(nickname=user.nickname).count() > 0

    def is_subscribed(self, user):
        return self.subscribed.filter(subscribes.c.subscribed_id == user.id).count() > 0

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
