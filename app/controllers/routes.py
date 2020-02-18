from flask import render_template, request, jsonify, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user

from app.models.forms import LoginForm
from app.models.tables import User

from app import app, db, lm

import logging

logging.basicConfig(level=logging.INFO)


@lm.user_loader
def load_user(id_user):
    return User.query.get(id_user)


@lm.unauthorized_handler
def unauthorized():
    """ Redirecionar usuários não autenticados """
    flash('Você deve estar autenticado para ver esta página')
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':

        if form.validate_on_submit():
            user = User.query.filter_by(
                username=form.data.get('username')
            ).first()

            if user and user.password == form.data.get('password'):
                login_user(user)
                logging.info(f'<USER {user.username} LOGGED IN>')
                flash('Autenticação bem sucedida')
                return redirect(url_for('index'))
            else:
                logging.warn(f'<USER {user.username} FAILS ON LOG IN>')
                flash('Erro ao autenticar')
        else:
            logging.warn(f'<APP ERRORS: {form.errors}>')
            flash('Erro na validação dos dados')

    return render_template('login.html', login_form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Você saiu')
    logging.info(f'<USER LOGGED OUT>')
    return redirect(url_for('index'))


DEFAULTS = {
    'name': 'eduardo',
    'email': 'edugenix@gmail.com',
    'username': 'eduns',
    'password': 'passwd'
}


@app.route('/signup/')
def register():
    user = User(
        DEFAULTS.get('username'),
        DEFAULTS.get('password'),
        DEFAULTS.get('name'),
        DEFAULTS.get('email')
    )

    db.session.add(user)
    db.session.commit()
    return jsonify('ok')


@app.route('/users/')
@app.route('/users/<user_str>')
def get_users(user_str=None):
    result = None

    if user_str is None:
        users = User.query.all()

        result = []
        for user in users:
            result.append({
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'password': user.password,
            })
    else:
        user = User.query.filter_by(username=user_str).first()
        result = {
            'name': user.name,
            'email': user.email,
            'username': user.username,
            'password': user.password,
        }

    return jsonify(result)
