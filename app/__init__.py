from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

db = SQLAlchemy()
lm = LoginManager()
mail = Mail()


def page_not_found(err):
    """ Renderizar responses htttp status 404 """

    if not err.response:
        err.response = {
            'title': 'Página não encontrada',
            'message': 'Desculpe, está página não foi encontrada :('
        }

    return render_template('page_not_found.html', response=err.response), 404


def access_denied(err):
    """ Renderizar responses http status 403 """

    return render_template('access_denied.html', response=err.response), 403


def add_header(response):
    """ Adiciona atributos ao header response da request """

    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate,\
        post-check=0, pre-check=0')
    return response


def create_app():
    """ Inicializa o app """

    app = Flask('FlipNews', instance_relative_config=False)

    # Aplica configurações
    app.config.from_object('config')

    # Inicializa as extensões ao app
    db.init_app(app)
    lm.init_app(app)
    mail.init_app(app)

    with app.app_context():
        # Importa e registra os Blueprints
        from app.controllers.main_routes import main_bp
        from app.controllers.users_routes import users_bp
        from app.controllers.news_routes import news_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(news_bp)

        # Registra os erros respectivos aos seus status codes
        app.register_error_handler(404, page_not_found)
        app.register_error_handler(403, access_denied)

        # Registra as funções executadas depois da request
        app.after_request(add_header)

        db.create_all()

        return app
