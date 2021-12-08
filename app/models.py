from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class InCom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    order_number = db.Column(db.String(140))
    product_type = db.Column(db.String(140))
    model = db.Column(db.String(140))
    cause = db.Column(db.String(140))
    detection_area = db.Column(db.String(140))
    description = db.Column(db.String(140))
    registration_status = db.Column(db.String(140), default='OTWARTE')

    def __repr__(self):
        return f'RW: {self.id},{self.user_id},{self.timestamp},{self.order_number},{self.product_type},{self.model}, ' \
               f'{self.cause}, {self.detection_area}, {self.description}, {self.registration_status}'


class Models(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_model = db.Column(db.String(140))


class Types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(140))


class Causes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cause_type = db.Column(db.String(140))


class DetectionAreas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    detection_area = db.Column(db.String(140))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
