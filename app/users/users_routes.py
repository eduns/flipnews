from flask import (
    Blueprint, render_template, render_template_string, jsonify, redirect,
    url_for, request, flash, current_app as app
)
from flask_assets import Environment
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
                     template_folder='templates',
                     static_folder='static')

assets = Environment(app)


@lm.user_loader
def load_user(id_user):
    """ Busca o usuário relacionado ao `id_user` da sessão """
    if id_user is not None:
        return User.query.get(id_user)


@lm.unauthorized_handler
def unauthorized():
    """ Redirecionar usuários não autenticados """
    flash('Você deve estar autenticado para ver esta página')
    return redirect(url_for('users_bp.signin', next=request.endpoint))


@users_bp.route('/', methods=['GET'])
@login_required
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))


@users_bp.route('/view/', methods=['GET'])
@login_required
def list_users():
    """ Lista todos os usuários """
    users = User.query.with_entities(
        User.user_id, User.username
    ).all()
    return render_template("users_list_users.html", users=users)


@users_bp.route('/view/<int:user_id>', methods=['GET'])
@login_required
def show_user(user_id):
    """ Carrega o usuário pelo respectivo `user_id` """
    user = User.query.get(user_id)
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
                    return redirect(url_for(next_url))

                flash(f'Bem-vindo(a), {user.username}!')
                return redirect(url_for('news_bp.show_articles'))
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

            flash('Seja bem-vindo(a)!')
            return redirect(url_for('main_bp.index'))
        else:
            logging.warn(f'[APP ERRORS: {signup_form.errors}]')
            flash('Erro na validação dos dados')

    return render_template('users_signup.html',
                           signup_form=signup_form,
                           title='Criar conta | FlipNews')
