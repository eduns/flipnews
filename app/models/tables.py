from app import db


class User(db.Model):
    """ Classe de usuário """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    _password = db.Column(db.String(), nullable=False)
    _is_admin = db.Column(db.Boolean(), default=False)

    # Relacionamento com a tabela Post
    posts = db.relationship('Post', backref='author', lazy=True)

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


class Post(db.Model):
    """ Classe de notícia """
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    image_name = db.Column(db.String(), nullable=True)
    author_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'),
                          nullable=False)

    def __init__(self, title, text, created_at, image_name, author_id):
        self.title = title
        self.text = text
        self.created_at = created_at
        self.image_name = image_name
        self.author_id = author_id

    def __repr__(self):
        return f'<Post {self.post_id}>'
