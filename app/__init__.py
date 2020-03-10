from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager

db = SQLAlchemy()
lm = LoginManager()
migrate = Migrate()


def page_not_found(err):
    """ Renderizar erros 404 """

    if not err.response:
        err.response = {
            'title': 'Página não encontrada',
            'message': 'Desculpe, está página não foi encontrada :('
        }

    return render_template('page_not_found.html', response=err.response), 404

def access_denied(err):
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
    migrate.init_app(app, db)

    with app.app_context():
        # Importa e registra os Blueprints
        from app.main_routes import main_bp
        from app.users_routes import users_bp
        from app.news_routes import news_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(news_bp)

        # Registra os erros respectivos aos seus status codes
        app.register_error_handler(404, page_not_found)
        app.register_error_handler(403, access_denied)

        app.after_request(add_header)

        # Adiciona o comando do db ao app
        manager = Manager(app)
        manager.add_command('db', MigrateCommand)

        return app
