from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import IMAGES
from wtforms import (
    StringField, PasswordField, BooleanField, TextAreaField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms.widgets import PasswordInput


class UserProfileForm(FlaskForm):
    """ Formulário das informações de usuário """

    name = StringField('Nome', validators=[
        DataRequired(message='Insira seu o nome')
    ])

    email = StringField('E-mail', validators=[
        DataRequired(message='Preencha o seu e-mail'),
        Email(message='Insira um e-mail válido')
    ])

    username = StringField('Usuário', validators=[
        DataRequired(message='Insira o nome de usuário'),
        Length(min=5, max=30,
               message='O nome de usuário deve ter pelo menos 5 caracteres\
                e no máximo 30')
    ])

    password = PasswordField('Senha', validators=[
        DataRequired(message='Insira a senha'),
        Length(min=6, message='Insira uma senha de pelo menos 6 caracteres')
    ], widget=PasswordInput(hide_value=False))


class SignupForm(UserProfileForm):
    """ Formulário de cadastro de usuários """

    confirm_password = PasswordField('Confirme a senha', validators=[
        DataRequired(message='Insira a confirmação de senha'),
        EqualTo('password', message='As senhas não correspondem')
    ])

    is_admin = BooleanField('Administrador')


class EditUserProfileForm(UserProfileForm):
    """ Formulário de atualização de dados do usuário """

    is_admin = BooleanField('Administrador')


class SigninForm(FlaskForm):
    """ Formulário de autenticação de usuários """

    email = StringField('E-mail', validators=[
        DataRequired(message='Preencha o e-mail'),
        Email(message='Preencha com um e-mail válido')
    ])

    password = PasswordField('Senha', validators=[
        DataRequired(message='Preencha a senha')
    ])

    remember_me = BooleanField()


class PostForm(FlaskForm):
    """ Formulário de cadastro de notícia """

    title = StringField('Título', validators=[
        DataRequired(message='Insira o título desta notícia')
    ])

    text = TextAreaField('Texto', validators=[
        DataRequired('Insira o texto desta notícia')
    ])

    image = FileField('Imagem', validators=[
        FileAllowed(IMAGES, f'Escolha imagens válidas. Formatos permitidos: \
            {", ".join(IMAGES)}')
    ])
