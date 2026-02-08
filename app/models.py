from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(32), default='operator')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(64), unique=True, index=True)
    model = db.Column(db.String(128))
    notes = db.Column(db.Text)


class Reception(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    received_by = db.Column(db.String(128))
    user_situm = db.Column(db.String(128))
    name = db.Column(db.String(128))
    phone = db.Column(db.String(64))
    device_imei = db.Column(db.String(64))
    notes = db.Column(db.Text)


class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_to = db.Column(db.String(128))
    user_situm = db.Column(db.String(128))
    name = db.Column(db.String(128))
    phone = db.Column(db.String(64))
    device_imei = db.Column(db.String(64))
    notes = db.Column(db.Text)


class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    reported_by = db.Column(db.String(128))
    phone = db.Column(db.String(64))
    file_path = db.Column(db.String(256))
    device_imei = db.Column(db.String(64))
