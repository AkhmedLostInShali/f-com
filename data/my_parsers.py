import datetime

from flask_restful import reqparse


class PublicationParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('id', required=False, type=int)
        self.add_argument('title', required=True)
        self.add_argument('photo', required=True)
        self.add_argument('description', required=False)
        self.add_argument('cheers', type=int, required=False)
        self.add_argument('publication_date', required=False, type=datetime.datetime)
        self.add_argument('author', required=True, type=int)


class UserParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('id', required=False, type=int)
        self.add_argument('email', required=True)
        self.add_argument('password', required=True)
        self.add_argument('password_again', required=True)
        self.add_argument('nickname', required=True)
        self.add_argument('avatar', required=True)
        self.add_argument('surname', required=False)
        self.add_argument('name', required=False)
        self.add_argument('age', required=False, type=int)
        self.add_argument('portrayal', required=False)
        self.add_argument('speciality', required=False)
        self.add_argument('rank', required=False)
        self.add_argument('city_from', required=False)
