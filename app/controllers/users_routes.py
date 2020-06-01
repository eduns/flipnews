from flask import (
    Blueprint, render_template, render_template_string, jsonify, redirect,
    url_for, request, flash, abort, current_app as app
)
from flask_login import (
    login_required, login_user, logout_user, current_user
)

# Models
from app.models.forms import (
    UserProfileForm, SigninForm, SignupForm, EditUserProfileForm
)
from app.models.tables import User

from app import lm, db

import logging
logging.basicConfig(level=logging.INFO)


users_bp = Blueprint('users_bp', __name__, url_prefix='/users',
                     template_folder='../templates/users',
                     static_folder='../static')


def check_restricted_fields(user_form, user):
    if user_form.password.raw_data is None:
        user_form.password.data = user._password

    if user_form.is_admin.raw_data is None:
        user_form.is_admin.data = user.is_admin()


@lm.user_loader
def load_user(user_id):
    """ Busca o usuário relacionado ao `user_id` da sessão """

    if user_id is not None:
        return User.query.get(user_id)


@lm.unauthorized_handler
def unauthorized():
    """ Redirecionar usuários não autenticados """

    flash('Você deve estar autenticado para ver esta página',
          category='warning')
    return redirect(url_for('users_bp.signin', next=request.path))


@users_bp.route('/management/', methods=['GET'])
@login_required
def show_users():
    """ Listar todos os usuários """

    if not current_user.is_admin():
        response = {
            'title': 'Acesso restrito',
            'message': 'Você não possui permissão para acessar esta página'
        }
        abort(403, response=response)

    users = User.query.with_entities(
        User.user_id, User.username
    ).all()

    return render_template('users_show_users.html', users=users)


@users_bp.route('/<username>/edit/', methods=['GET', 'POST'])
@login_required
def update_user(username):
    """ Editar informações do usuário """

    user = User.query.filter_by(username=username).first()
    user_form = EditUserProfileForm(obj=user)

    if user:

        check_restricted_fields(user_form, user)

        if request.method == 'POST':

            if request.referrer == request.url:

                if user_form.validate_on_submit():

                    user_name = user_form.name.data
                    user_email = user_form.email.data
                    user_username = user_form.username.data
                    user_password = user_form.password.data
                    user_is_admin = user_form.is_admin.data

                    user.name = user_name
                    user.email = user_email
                    user.username = user_username
                    user._password = user_password
                    user._is_admin = user_is_admin

                    db.session.commit()

                    flash(f'Dados de {user_username} atualizados com sucesso',
                          category='success')
                    return redirect(url_for('.show_users'))

                else:
                    logging.warn(f'ERRORS: {user_form.errors}')

    else:
        response = {
            'title': 'Usuários',
            'message': 'Usuário não encontrado'
        }
        abort(404, response=response)

    return render_template('users_edit_user.html',
                           user=user,
                           user_form=user_form,
                           title="Editar usuário | FlipNews")


@users_bp.route('/delete/<username>', methods=['POST'])
def delete_user(username):
    """ Apaga o usuário pelo seu `username` """

    user = User.query.filter_by(username=username).first()

    if user:
        db.session.delete(user)
        db.session.commit()

        flash(f'Usuário {username} apagado com sucesso', category='success')
    else:
        response = {
            'title': 'Usuário não encontrado',
            'message': 'Este usuário não existe'
        }
        abort(404, response=response)

    return redirect(url_for('.show_users'))


@users_bp.route('/auth/signout/')
def signout():
    """ Encerrar sessão do usuário """

    if not current_user.is_authenticated:
        response = {
            'title': 'Acesso não autorizado',
            'message': 'Você não tem permissão para acessar este recurso'
        }
        abort(403, response=response)

    logging.info(f'[{current_user} SIGNED OUT]')
    logout_user()
    flash('Você saiu', category='success')
    return redirect(url_for('users_bp.signin'))


@users_bp.route('/auth/signin/', methods=['GET', 'POST'])
def signin():
    """ Autenticação de usuários """

    if current_user.is_authenticated:
        return redirect(url_for('news_bp.show_posts'))

    signin_form = SigninForm()

    if request.method == 'POST':

        if signin_form.validate_on_submit():
            email = signin_form.data.get('email')
            password = signin_form.data.get('password')

            user = User.query.filter_by(email=email).first()

            if user and user._password == password:
                login_user(user)
                logging.info(f'[{user} SIGNED IN]')

                next_url = request.args.get('next')

                if next_url:
                    return redirect(next_url)

                return redirect(url_for('news_bp.show_posts'))
            else:
                flash('Usuário ou senha inválidos!', category='warning')
        else:
            flash('Erro na validação dos dados', category='warning')

    return render_template('users_signin.html',
                           signin_form=signin_form,
                           template_class='signin-page',
                           page_title='Entrar | FlipNews')


@users_bp.route('/auth/signup/', methods=['GET', 'POST'])
@login_required
def signup():
    """ Cadastro de usuários """

    signup_form = SignupForm()

    if request.method == 'POST':

        if signup_form.validate_on_submit():
            name = signup_form.data.get('name')
            email = signup_form.data.get('email')
            username = signup_form.data.get('username')
            password = signup_form.data.get('password')
            is_admin = signup_form.data.get('is_admin')

            user = User(
                name=name,
                email=email,
                username=username,
                password=password,
                is_admin=is_admin
            )

            db.session.add(user)
            db.session.commit()

            flash(f'Usuário {username} criado com sucesso', category='success')
            return redirect(url_for('.signup'))
        else:
            logging.warn(f'[APP ERRORS: {signup_form.errors}]')
            flash('Erro na validação dos dados', category='warning')

    return render_template('users_signup.html',
                           signup_form=signup_form,
                           template_class='signup-page',
                           page_title='Criar novo usuário | FlipNews')
