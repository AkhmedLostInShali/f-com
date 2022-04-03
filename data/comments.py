import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    send_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    sender = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    receiver = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("publications.id"))
    user = orm.relation('User')
    art = orm.relation('Publication')
