from app import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    _password = db.Column(db.String(), nullable=False)
    _is_admin = db.Column(db.Boolean(), default=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return True

    def is_admin(self):
        return self._is_admin

    def get_id(self):
        return f'{self.user_id}'

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self._password = password

    def __repr__(self):
        return f'<User {self.username}>'
