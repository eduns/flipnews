from flask import (
    Blueprint, render_template, render_template_string, jsonify, redirect,
    url_for, request, flash, abort, current_app as app
)
from flask_login import (
    login_required, login_user, logout_user, current_user,
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
                     template_folder='templates/users',
                     static_folder='static')


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

    flash('Você deve estar autenticado para ver esta página')
    return redirect(url_for('users_bp.signin', next=request.path))


@users_bp.route('/admin/management/', methods=['GET'])
@login_required
def show_users():
    """ Listar todos os usuários """

    if not current_user.is_admin():
        flash('Você não tem permissão para acessar esta página!')
        return redirect(url_for('news_bp.show_posts'))

    users = User.query.with_entities(
        User.user_id, User.username
    ).all()

    return render_template("users_list_users.html", users=users)


@users_bp.route('/<username>/details/', methods=['GET'])
@login_required
def show_user(username):
    """ Carrega o usuário pelo respectivo `username` """

    user = User.query.filter_by(username=username).first()

    if not user:
        response = {
            'title': 'Usuário inexistente',
            'message': 'Desculpe, este usuário não existe :('
        }
        abort(404, response=response)

    return render_template('users_view_user.html', user=user)


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

                    flash(f'Dados de {user_username} atualizados com sucesso')
                    return redirect(url_for('.show_users'))

                else:
                    logging.warn(f'ERRORS: {user_form.errors}')

    else:
        response = {
            'title': 'Usuário não encontrado',
            'message': 'Este usuário não existe'
        }
        abort(404, response=response)

    return render_template('users_edit_user.html',
                           user_form=user_form,
                           title="Editar usuário | FlipNews",
                           form_title="Editar informações",
                           form_action=url_for('.update_user',
                                               username=user.username))


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """ Apaga o usuário pelo seu `user_id` """

    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

        flash('Usuário apagado com sucesso')

    else:
        response = {
            'title': 'Usuário não encontrado',
            'message': 'Este usuário não existe'
        }
        abort(404, response=response)

    return redirect(url_for('.show_users'))


@users_bp.route('/auth/signout/')
@login_required
def signout():
    """ Encerrar sessão do usuário """
    logging.info(f'[USER {current_user.username} SIGNED OUT]')
    logout_user()
    flash('Você saiu')
    return redirect(url_for('users_bp.signin'))


@users_bp.route('/auth/signin/', methods=['GET', 'POST'])
def signin():
    """ Autenticação de usuários """

    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    signin_form = SigninForm()

    if request.method == 'POST':

        if signin_form.validate_on_submit():
            email = signin_form.data.get('email')
            password = signin_form.data.get('password')

            user = User.query.filter_by(email=email).first()

            if user and user._password == password:
                login_user(user)
                logging.info(f'[USER {user.username} SIGNED IN]')

                next_url = request.args.get('next')

                if next_url:
                    return redirect(next_url)

                flash(f'Bem-vindo(a), {user.username}!')
                return redirect(url_for('news_bp.show_posts'))
            else:
                flash('Usuário ou senha inválidos!')
        else:
            flash('Erro na validação dos dados')

    return render_template('users_signin.html',
                           signin_form=signin_form,
                           title='Entrar | FlipNews')


@users_bp.route('/auth/signup/', methods=['GET', 'POST'])
def signup():
    """ Cadastro de usuários """

    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    signup_form = SignupForm()

    if request.method == 'POST':

        if signup_form.validate_on_submit():
            name = signup_form.data.get('name')
            email = signup_form.data.get('email')
            username = signup_form.data.get('username')
            password = signup_form.data.get('password')

            user = User(
                name=name,
                email=email,
                username=username,
                password=password
            )

            db.session.add(user)
            db.session.commit()

            flash(f'Se autentique para  continuar')
            return redirect(url_for('users_bp.signin'))
        else:
            logging.warn(f'[APP ERRORS: {signup_form.errors}]')
            flash('Erro na validação dos dados')

    return render_template('users_signup.html',
                           signup_form=signup_form,
                           title='Criar conta | FlipNews')
