import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Publication(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'publications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cheers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    # comments =
