from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    security_answer1 = db.Column(db.String(256))
    security_answer2 = db.Column(db.String(256))
    security_answer3 = db.Column(db.String(256))

    data_sets = db.relationship('DataSet', backref='user', lazy=True)
    profile = db.relationship('UserProfile', backref='user', uselist=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
        if 'security_answer1' in kwargs:
            self.set_security_answer1(kwargs['security_answer1'])
        if 'security_answer2' in kwargs:
            self.set_security_answer2(kwargs['security_answer2'])
        if 'security_answer3' in kwargs:
            self.set_security_answer3(kwargs['security_answer3'])

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_security_answer1(self, answer):
        self.security_answer1 = generate_password_hash(answer)

    def set_security_answer2(self, answer):
        self.security_answer2 = generate_password_hash(answer)

    def set_security_answer3(self, answer):
        self.security_answer3 = generate_password_hash(answer)

    def check_security_answer1(self, answer):
        return self.security_answer1 and check_password_hash(self.security_answer1, answer)

    def check_security_answer2(self, answer):
        return self.security_answer2 and check_password_hash(self.security_answer2, answer)

    def check_security_answer3(self, answer):
        return self.security_answer3 and check_password_hash(self.security_answer3, answer)

    def temp_folder(self) -> str:
        from app.modules.auth.services import AuthenticationService
        return AuthenticationService().temp_folder_by_user(self)
