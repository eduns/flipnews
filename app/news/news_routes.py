from flask import (
    Blueprint, render_template, jsonify, request, flash, current_app as app
)
from flask_login import (
    login_required, current_user
)
from werkzeug.utils import secure_filename

from app import db

from app.models.forms import ArticleForm
from app.models.tables import Article

from uuid import uuid4
import logging
from os import path

from datetime import datetime

news_bp = Blueprint('news_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/news')


@news_bp.route('/', methods=['GET'])
def index():
    """ Rota de notícias """
    return render_template('news.html')


@news_bp.route('/articles/', methods=['GET'])
def show_articles():
    """ Carrega todas as notícias """
    articles = Article.query.with_entities(
        Article.article_id, Article.title, Article.image_name
    ).all()
    return render_template('news_list_articles.html', articles=articles)


@news_bp.route('/articles/view/<int:article_id>', methods=['GET'])
@login_required
def show_article(article_id):
    """ Carrega o artigo pelo respectivo `article_id` """
    article = Article.query.get(article_id)
    return render_template('news_view_article.html', article=article)


@news_bp.route('/articles/post/', methods=['GET', 'POST'])
@login_required
def post_article():
    """ Cadastrar novas notícias """
    article_form = ArticleForm()

    if request.method == 'POST':

        if article_form.validate_on_submit():
            title = article_form.data.get('title')
            text = article_form.data.get('text')
            image = request.files.get('image')
            filename = None

            created_at = datetime.now()

            if image:
                filename = f'{uuid4()}_{secure_filename(image.filename)}'
                image_url = path.join(path.curdir, 'images', filename)
                image.save(image_url)
                flash('Upload da imagem concluído')

            article = Article(
                title=title,
                text=text,
                created_at=created_at,
                image_name=filename,
                author_id=current_user.get_id()
            )

            db.session.add(article)
            db.session.commit()

            flash('Notícia postada com sucesso')

        else:
            logging.warn(f'ERRORS: {article_form.errors}')

    return render_template('news_edit_article.html',
                           article_form=article_form,
                           title="Postar nova notícia | FlipNews")
