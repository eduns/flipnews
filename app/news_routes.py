from flask import (
    Blueprint, render_template, jsonify, request, redirect,
    abort, url_for, flash, current_app as app
)
from flask_login import (
    login_required, current_user
)
from werkzeug.utils import secure_filename

from app import db

from app.models.forms import ArticleForm
from app.models.tables import Article

from uuid import uuid4
from os import system
import logging
from datetime import datetime

news_bp = Blueprint('news_bp', __name__,
                    template_folder='templates/news',
                    static_folder='static',
                    url_prefix='/news')


def get_secure_image_name(article_image):
    """ Define um nome seguro para a imagem """
    return f'{uuid4()}_{secure_filename(article_image.filename)}'


def get_image_url(image_name):
    """ Retorna a url de onde a imagem será salva """
    return f"{app.config['UPLOADED_NEWS_IMAGES_DEST']}/{image_name}"


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


@news_bp.route('/articles/view/<int:article_id>',
               methods=['GET', 'POST', 'DELETE'])
@login_required
def show_article(article_id):
    """ Carrega o artigo pelo respectivo `article_id` """
    article = Article.query.get(article_id)

    if not article:
        response = {
            'title': 'Conteúdo não encontrado',
            'message': 'Desculpe, este conteúdo não existe :('
        }
        abort(404, response=response)

    return render_template('news_view_article.html', article=article)


@news_bp.route('/articles/post/', methods=['GET', 'POST'])
@login_required
def post_article():
    """ Cadastrar novas notícias """
    article_form = ArticleForm()

    if request.method == 'POST':

        if article_form.validate_on_submit():
            article_title = article_form.data.get('title')
            article_text = article_form.data.get('text')
            article_image = request.files.get('image')
            article_created_at = datetime.now()
            article_image_name = None

            if article_image:
                article_image_name = get_secure_image_name(article_image)
                image_url = get_image_url(article_image_name)

                article_image.save(image_url)
                flash('Upload da imagem concluído')

            article = Article(
                title=article_title,
                text=article_text,
                created_at=article_created_at,
                image_name=article_filename,
                author_id=current_user.get_id()
            )

            db.session.add(article)
            db.session.commit()

            flash('Notícia postada com sucesso')
            return redirect(url_for('.post_article'))

        else:
            logging.warn(f'ERRORS: {article_form.errors}')

    return render_template('news_edit_article.html',
                           article_form=article_form,
                           title="Nova notícia | FlipNews",
                           form_title="Postar nova notícia")


@news_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
def update_article(article_id):
    image_name = None

    article = Article.query.get(article_id)
    article_form = ArticleForm(obj=article)

    if article:
        image_name = article.image_name

        if request.method == 'POST':

            if request.referrer == request.url:

                if article_form.validate_on_submit():

                    article_title = article_form.title.data
                    article_text = article_form.text.data
                    article_image = request.files.get('image')
                    article_image_name = None

                    article.title = article_title
                    article.text = article_text

                    if article_image:
                        article_image_name = get_secure_image_name(
                            article_image)
                        image_url = get_image_url(article_image_name)

                        article.image_name = article_image_name

                        article_image.save(image_url)
                        flash('Upload da nova imagem concluído')

                        system(f'rm {app.config["UPLOADED_NEWS_IMAGES_DEST"]}/\
                        {image_name}')

                    db.session.commit()

                    flash('Notícia atualizada com sucesso')
                    return redirect(url_for('.show_articles'))

                else:
                    logging.warn(f'ERRORS: {article_form.errors}')

    else:
        flash('Notícia inexistente!')
        return redirect(url_for('.show_articles'))

    return render_template('news_edit_article.html',
                           article_form=article_form,
                           image_name=image_name,
                           title="Editar Notícia | FlipNews",
                           form_title="Editar notícia",
                           form_action=url_for(
                               '.update_article',
                               article_id=article.article_id))


@news_bp.route('/articles/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get(article_id)
    if article:
        db.session.delete(article)
        db.session.commit()

        system(f'rm {app.config["UPLOADED_NEWS_IMAGES_DEST"]}/\
        {article.image_name}')

        flash('Notícia apagada com sucesso')
        return redirect(url_for('.show_articles'))
    else:
        flash('Erro ao apagar a notícia')
        return redirect(request.referrer)
