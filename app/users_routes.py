from flask import (
    Blueprint, render_template, render_template_string, jsonify, redirect,
    url_for, request, flash, current_app as app
)
from flask_login import (
    login_required, login_user, logout_user, current_user,
)

# Models
from app.models.forms import SigninForm, SignupForm
from app.models.tables import User

from app import lm, db


import logging
logging.basicConfig(level=logging.INFO)


users_bp = Blueprint('users_bp', __name__, url_prefix='/users',
                     template_folder='templates/users',
                     static_folder='static')


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


@users_bp.route('/', methods=['GET'])
@login_required
def show_users():
    """ Lista todos os usuários """
    if current_user.is_admin():
        users = User.query.with_entities(
            User.user_id, User.username
        ).all()
        return render_template("users_list_users.html", users=users)

    flash('Você não tem permissão para acessar esta página!')
    return redirect(url_for('news_bp.show_posts'))


@users_bp.route('/<username>/details', methods=['GET'])
@login_required
def show_user(username):
    """ Carrega o usuário pelo respectivo `user_id` """
    user = User.query.filter_by(username=username).first()
    return render_template('users_view_user.html', user=user)


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
