from flask_restful import reqparse


class PublicationParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        # self.add_argument('id', required=False, type=int)
        # self.add_argument('job', required=True)
        # self.add_argument('work_size', required=True, type=int)
        # self.add_argument('collaborators', required=True)
        # self.add_argument('is_finished', required=True, type=bool)
        # self.add_argument('team_leader', required=True, type=int)


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
