from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)

    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role
        }

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)

    slots = db.relationship('Slot', backref='location', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    reservations = db.relationship('Reservation', backref='slot', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'name': self.name,
            'is_available': self.is_available
        }

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    reservation_time = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'slot_id': self.slot_id,
            'user_id': self.user_id,
            'reservation_time': self.reservation_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status
        }