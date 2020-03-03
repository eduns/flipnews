from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import IMAGES
from wtforms import (
    StringField, PasswordField, BooleanField, TextAreaField
)
from wtforms.validators import DataRequired, Email, Length


class SigninForm(FlaskForm):
    """ Formulário de autenticação de usuários """
    email = StringField('email', validators=[
        DataRequired(message='Preencha o e-mail'),
        Email(message='Preencha com um e-mail válido')
    ])

    password = PasswordField('password', validators=[
        DataRequired(message='Preencha a senha')
    ])

    remember_me = BooleanField()


class SignupForm(FlaskForm):
    """ Formulário de cadastro de usuários """
    name = StringField('name', validators=[
        DataRequired(message='Insira seu o nome')
    ])

    email = StringField('email', validators=[
        DataRequired(message='Preencha o seu e-mail'),
        Email(message='Insira um e-mail válido')
    ])

    username = StringField('username', validators=[
        DataRequired(message='Insira o nome de usuário'),
        Length(min=5, max=30,
               message='O nome de usuário de pelo menos 5 caracteres\
                e no máximo 30')
    ])

    password = PasswordField('password', validators=[
        DataRequired(message='Insira a senha'),
        Length(min=6, message='Insira uma senha de pelo menos 6 caracteres')
    ])


class PostForm(FlaskForm):
    """ Formulário de cadastro de notícia """
    title = StringField('Título da notícia', validators=[
        DataRequired(message='Insira o título desta notícia')
    ])

    text = TextAreaField('Texto da notícia', validators=[
        DataRequired('Insira o texto desta notícia')
    ])

    image = FileField('Imagem da notícia', validators=[
        FileAllowed(IMAGES, f'Escolha imagens válidas. Formatos permitidos: \
            {", ".join(IMAGES)}')
    ])
