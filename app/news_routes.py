from flask import (
    Blueprint, render_template, jsonify, request, redirect,
    abort, url_for, flash, current_app as app
)
from flask_login import (
    login_required, current_user
)
from werkzeug.utils import secure_filename

from app import db

from app.models.forms import PostForm
from app.models.tables import Post

from uuid import uuid4
from os import system
import logging
from datetime import datetime

news_bp = Blueprint('news_bp', __name__,
                    template_folder='templates/news',
                    static_folder='static',
                    url_prefix='/news')


def get_unique_image_name(post_image):
    """ Define um nome seguro e único para a imagem """

    return f'{uuid4()}_{secure_filename(post_image.filename)}'


def get_image_url(image_name):
    """ Retorna a url de onde a imagem será salva """

    return f"{app.config['UPLOADED_NEWS_IMAGES_DEST']}/{image_name}"


@news_bp.route('/', methods=['GET'])
def index():
    """ Rota de notícias """
    return render_template('news.html')


@news_bp.route('/posts/', methods=['GET'])
def show_posts():
    """ Carrega todas as notícias """

    posts = Post.query.with_entities(
        Post.post_id, Post.title, Post.image_name
    ).all()
    return render_template('news_show_posts.html', posts=posts)


@news_bp.route('/posts/view/<int:post_id>',
               methods=['GET', 'POST'])
@login_required
def show_post(post_id):
    """ Carrega o post pelo respectivo `post_id` """

    post = Post.query.get(post_id)

    if not post:
        response = {
            'title': 'Conteúdo não encontrado',
            'message': 'Desculpe, este conteúdo não existe :('
        }
        abort(404, response=response)

    return render_template('news_view_post.html', post=post)


@news_bp.route('/posts/add/', methods=['GET', 'POST'])
@login_required
def add_post():
    """ Cadastrar novas notícias """

    post_form = PostForm()

    if request.method == 'POST':

        if post_form.validate_on_submit():
            post_title = post_form.data.get('title')
            post_text = post_form.data.get('text')
            post_image = request.files.get('image')
            post_created_at = datetime.now()
            post_image_name = None

            if post_image:
                post_image_name = get_unique_image_name(post_image)
                image_url = get_image_url(post_image_name)

                post_image.save(image_url)
                flash('Upload da imagem concluído')

            post = Post(
                title=post_title,
                text=post_text,
                created_at=post_created_at,
                image_name=post_filename,
                author_id=current_user.get_id()
            )

            db.session.add(post)
            db.session.commit()

            flash('Notícia postada com sucesso')
            return redirect(url_for('.add_post'))

        else:
            logging.warn(f'ERRORS: {post_form.errors}')

    return render_template('news_edit_post.html',
                           post_form=post_form,
                           title="Nova notícia | FlipNews",
                           form_title="Postar nova notícia")


@news_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    """ Atualiza os dados da notícia pelo `post_id` """

    image_name = None

    post = Post.query.get(post_id)
    post_form = PostForm(obj=post)

    if post:
        image_name = post.image_name

        if request.method == 'POST':

            if request.referrer == request.url:

                if post_form.validate_on_submit():

                    post_title = post_form.title.data
                    post_text = post_form.text.data
                    post_image = request.files.get('image')
                    post_image_name = None

                    post.title = post_title
                    post.text = post_text

                    if post_image:
                        post_image_name = get_unique_image_name(
                            post_image)
                        image_url = get_image_url(post_image_name)

                        post.image_name = post_image_name

                        post_image.save(image_url)
                        flash('Upload da nova imagem concluído')

                        system(f'rm {app.config["UPLOADED_NEWS_IMAGES_DEST"]}/\
                        {image_name}')

                    db.session.commit()

                    flash('Notícia atualizada com sucesso')
                    return redirect(url_for('.show_posts'))

                else:
                    logging.warn(f'ERRORS: {post_form.errors}')

    else:
        flash('Notícia inexistente!')
        return redirect(url_for('.show_posts'))

    return render_template('news_edit_post.html',
                           post_form=post_form,
                           image_name=image_name,
                           title="Editar Notícia | FlipNews",
                           form_title="Editar notícia",
                           form_action=url_for('.update_post',
                                               post_id=post.post_id))


@news_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """ Apaga a notícia pelo seu `post_id` """

    post = Post.query.get(post_id)

    if post:
        db.session.delete(post)
        db.session.commit()

        system(f'rm {app.config["UPLOADED_NEWS_IMAGES_DEST"]}/\
        {post.image_name}')

        flash('Notícia apagada com sucesso')
        return redirect(url_for('.show_posts'))

    else:
        flash('Erro ao apagar a notícia')

    return redirect(request.referrer)
