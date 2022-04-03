import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    send_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    sender = orm.relationship("User", foreign_keys='Message.sender_id')
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    receiver = orm.relationship("User", foreign_keys='Message.receiver_id')
    # user = orm.relation('User')
    # stakeholder = relationship("Company", foreign_keys='stakeholder_id')
