from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.postgresql import BYTEA


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.LargeBinary, nullable=False,
                           default=b'')  # Profile picture
    off_balance = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"User('{self.username}')"


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_of_submission = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    location = db.Column(db.String, nullable=True)  # add this line

    def __repr__(self):
        return f"Attendance('{self.user_id}', '{self.date}', '{self.status}', '{self.time_of_submission}', '{self.location}')"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    assigned_to = db.Column(db.String(20), nullable=False)
    created_by = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)  # New field

    def __repr__(self):
        return f"Task('{self.task_name}', '{self.assigned_to}', '{self.created_by}')"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
