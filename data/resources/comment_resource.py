from flask import jsonify, request
from flask_restful import abort, Resource
from .. import db_session, my_parsers
from ..comments import Comment
import logging
import datetime

logging.basicConfig(level=logging.INFO)

parser = my_parsers.CommentParser()


def abort_if_comment_not_found(comment_id):
    session = db_session.create_session()
    comment = session.query(Comment).get(comment_id)
    if not comment:
        abort(404, message=f"Comment {comment_id} not found")


class CommentsResource(Resource):
    def get(self, comment_id):
        abort_if_comment_not_found(comment_id)
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        out_dict = comment.to_dict(only=('id', 'text', 'send_time', 'receiver', 'sender'))
        out_dict['user'] = comment.user.to_dict(only=('id', 'nickname', 'avatar'))
        return jsonify({'comment': out_dict})

    def delete(self, comment_id):
        abort_if_comment_not_found(comment_id)
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        # if users_id < 3:
        #     return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(comment)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, comment_id):
        abort_if_comment_not_found(comment_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        comment.text = request.json['text'] if request.json.get('text') else comment.text
        db_sess.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment).all()
        return jsonify({'comments': [comment.to_dict(only=['id', 'text', 'send_time', 'receiver', 'sender'])
                                     for comment in comments]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        comment = Comment()
        comment.text = args['text']
        comment.sender = args['sender']
        comment.receiver = args['receiver']
        comment.send_time = datetime.datetime.now()

        db_sess.add(comment)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class CommentsTreeResource(Resource):
    def get(self, publications_id):
        db_sess = db_session.create_session()
        comments = db_sess.query(Comment).filter(Comment.receiver == publications_id).all()
        out_list = []
        for comment in comments:
            out_dict = comment.to_dict(only=('id', 'text', 'send_time', 'receiver'))
            out_dict['user'] = comment.user.to_dict(only=('id', 'nickname', 'avatar'))
            out_list.append(out_dict)
        return jsonify({'comments': out_list})
