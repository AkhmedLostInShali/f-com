from flask import jsonify, request
from flask_restful import abort, Resource
from .. import db_session, my_parsers
from ..publications import Publication
import logging

logging.basicConfig(level=logging.INFO)

parser = my_parsers.PublicationParser()


def abort_if_publications_not_found(publications_id):
    session = db_session.create_session()
    publication = session.query(Publication).get(publications_id)
    if not publication:
        abort(404, message=f"Publication {publications_id} not found")


class PublicationsResource(Resource):
    def get(self, publications_id):
        abort_if_publications_not_found(publications_id)
        db_sess = db_session.create_session()
        publication = db_sess.query(Publication).get(publications_id)
        return jsonify({'publication': publication.to_dict()})

    def delete(self, publications_id):
        abort_if_publications_not_found(publications_id)
        db_sess = db_session.create_session()
        publication = db_sess.query(Publication).get(publications_id)
        if publications_id < 3:
            return jsonify({'error': "you can't delete main posts"})
        db_sess.delete(publication)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, publications_id):
        abort_if_publications_not_found(publications_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [publication.id for publication
                                                                 in db_sess.query(Publication).all()]:
            return jsonify({'error': 'Id already exists'})
        publication = db_sess.query(Publication).get(publications_id)
        publication.id = request.json['id'] if request.json.get('id') else publication.id
        publication.title = request.json['title'] if request.json.get('title') else publication.title
        publication.photo = request.json['photo'] if request.json.get('photo') else publication.photo
        publication.description = request.json['description'] if request.json.get('description')\
            else publication.description
        publication.cheers = request.json['cheers'] if request.json.get('cheers') else publication.cheers
        publication.publication_date = request.json['publication_date'] if request.json.get('publication_date')\
            else publication.publication_date
        db_sess.commit()
        return jsonify({'success': 'OK'})


class PublicationsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        publications = db_sess.query(Publication).all()
        return jsonify({'publications': [publication.to_dict(only=('id', 'photo', 'title', 'publication_date',
                                                                   'author'))
                                         for publication in publications]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(Publication).all()]:
            return jsonify({'error': 'Id already exists'})

        publication = Publication()
        if args.get('id'):
            publication.id = args.get('id')
        publication.title = args['title']
        publication.photo = args['photo']
        publication.description = args['description']
        publication.author = args['author']

        db_sess.add(publication)
        db_sess.commit()
        return jsonify({'success': 'OK'})
