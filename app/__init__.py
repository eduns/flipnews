from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager

db = SQLAlchemy()
lm = LoginManager()
migrate = Migrate()


def page_not_found():
    return render_template('page_not_found.html'), 404


def create_app():
    """ Inicializa o app """
    app = Flask(__name__, instance_relative_config=False)

    # Aplica configurações
    app.config.from_object('config')

    # Inicializa as dependências ao app
    db.init_app(app)
    lm.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Importa e registra os Blueprints
        from app.main_routes import main_bp
        from app.users.users_routes import users_bp
        from app.news.news_routes import news_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(news_bp)

        app.register_error_handler(404, page_not_found)

        # Adiciona o comando do db ao app
        manager = Manager(app)
        manager.add_command('db', MigrateCommand)

        return app
