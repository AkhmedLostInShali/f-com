from flask import jsonify, request
from flask_restful import abort, Resource
from sqlalchemy import and_
from .. import db_session, my_parsers
from ..messages import Message
import logging
import datetime

logging.basicConfig(level=logging.INFO)

parser = my_parsers.MessageParser()


def abort_if_message_not_found(message_id):
    session = db_session.create_session()
    message = session.query(Message).get(message_id)
    if not message:
        abort(404, message=f"Message {message_id} not found")


class MessagesResource(Resource):
    def get(self, message_id):
        abort_if_message_not_found(message_id)
        db_sess = db_session.create_session()
        message = db_sess.query(Message).get(message_id)
        out_dict = message.to_dict(only=('id', 'text', 'send_time', 'receiver_id', 'sender_id'))
        return jsonify({'message': out_dict})

    def delete(self, message_id):
        abort_if_message_not_found(message_id)
        db_sess = db_session.create_session()
        message = db_sess.query(Message).get(message_id)
        # if users_id < 3:
        #     return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(message)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, message_id):
        abort_if_message_not_found(message_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        message = db_sess.query(Message).get(message_id)
        message.text = request.json['text'] if request.json.get('text') else message.text
        db_sess.commit()
        return jsonify({'success': 'OK'})


class MessagesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        messages = db_sess.query(Message).all()
        return jsonify({'messages': [message.to_dict(only=['id', 'text', 'send_time', 'receiver_id', 'sender_id'])
                                     for message in messages]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        message = Message()
        message.text = args['text']
        message.sender_id = args['sender_id']
        message.receiver_id = args['receiver_id']
        message.send_time = datetime.datetime.now()

        db_sess.add(message)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class MessagesDialogResource(Resource):
    def get(self, sender, receiver):
        db_sess = db_session.create_session()
        logging.info(str(sender) + '-' + str(receiver))
        messages = db_sess.query(Message).filter(and_(Message.sender_id == sender, Message.receiver_id == receiver) |
                                                 and_(Message.sender_id == receiver, Message.receiver_id == sender)
                                                 ).all()
        return jsonify({'messages': [message.to_dict(only=['id', 'text', 'send_time', 'receiver_id', 'sender_id'])
                                     for message in messages]})
