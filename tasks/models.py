import datetime

from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


class Task(db.Model):
    """ Model representing task """
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    # Choice field
    state = db.Column(
        Enum('Новая', 'Запланированная', 'в Работе',
             'Завершённая', name='statuses', default='Новая')
    )
    due = db.Column(db.DateTime)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, data):
        """ Constructor """
        self.title = data.get('title')
        self.description = data.get('description')
        self.created_at = datetime.datetime.now()
        self.state = data.get('state')
        self.due = data.get('due')
        self.owner = data.get('owner')

    def save(self):
        """ Save instance """
        db.session.add(self)
        db.session.commit()
        db.session.flush()
        return self.id

    def update(self, data):
        """ Modify instance """
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        """ Delete instance """
        db.session.delete(self)
        db.session.commit()

    def __repr(self):
        return '<id {}>'.format(self.id)


class User(db.Model):
    """ Model representing user """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, data):
        """ Constructor """
        self.username = data.get('username')
        self.password = self.__generate_hash(data.get('password'))

    def save(self):
        """ Save row to DB """
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ Update row """
        for key, item in data.items():
            if key == 'password':
                self.password = self.__generate_hash(item)
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        """ Delete row from db """
        db.session.delete(self)
        db.session.commit()

    def __generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10).decode('utf-8')

    def check_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr(self):
        return '<id {}>'.format(self.id)

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def get_one_user(id):
        return User.query.get(id)
