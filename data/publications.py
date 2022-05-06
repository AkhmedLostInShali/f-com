import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table(
    'association',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('publications', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('publications.id')),
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')))


class Publication(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'publications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    reported = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    cheers = orm.relation("User",
                          secondary="association",
                          backref="cheered")
