from flask import url_for
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


# association_table = sqlalchemy.Table(
#     'user_to_user',
#     SqlAlchemyBase.metadata,
#     sqlalchemy.Column('subscriber_id', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('users.id')),
#     sqlalchemy.Column('creator_id', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('users.id')),
#     orm.relationship("User", foreign_keys='User.subscriber_id'),
#     orm.relationship("User", foreign_keys='User.creator_id'))


class UserToUser(SqlAlchemyBase):
    __tablename__ = 'user_to_user'
    subscriber_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), primary_key=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), primary_key=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    subscriber = orm.relationship("User", back_populates="subscribers", foreign_keys=[subscriber_id])
    creator = orm.relationship("User", back_populates="subscriptions", foreign_keys=[creator_id])


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

    subscriptions = orm.relation("UserToUser",
                                 back_populates="subscriber", foreign_keys='UserToUser.creator_id')
    subscribers = orm.relation("UserToUser",
                               back_populates="creator", foreign_keys='UserToUser.subscriber_id')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
