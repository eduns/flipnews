from flask import (
    Blueprint, render_template, jsonify, request, redirect,
    abort, url_for, flash, current_app as app
)
from flask_login import (
    login_required, current_user
)
from werkzeug.utils import secure_filename
from flask_mail import Message

from app import db, mail

from app.models.forms import PostForm
from app.models.tables import Post, User

from uuid import uuid4
from os import system
from sys import platform
import logging
from datetime import datetime

news_bp = Blueprint('news_bp', __name__, url_prefix='/news',
                    template_folder='../templates/news',
                    static_folder='../static')


def get_unique_image_name(post_image):
    """ Define um nome seguro e único para a imagem """

    return f'{uuid4()}_{secure_filename(post_image.filename)}'


def get_image_url(image_name):
    """ Retorna a url de onde a imagem será salva """

    return f"{app.config['UPLOADED_NEWS_IMAGES_DEST']}/{image_name}"


def send_email(post_title):
    """ Envia e-mail de nova notícia aos usuários """

    try:
        emails = User.query.with_entities(User.email).filter_by(
            _is_admin='f'
        ).all()

        for email in emails:
            message = Message(subject='Nova notícia disponível',
                              recipients=[email[0]],
                              body=post_title)

            mail.send(message)

        logging.info(f'MAIL SENT TO USERS')
    except Exception as ex:
        logging.error(ex.msg)


@news_bp.route('/posts/', methods=['GET'])
def show_posts():
    """ Carrega todas as notícias """

    posts = Post.query.with_entities(
        Post.post_id, Post.title, Post.image_name
    ).order_by(Post.post_id).all()

    return render_template('news_show_posts.html', posts=posts)


@news_bp.route('/posts/view/<int:post_id>', methods=['GET', 'POST'])
@login_required
def show_post(post_id):
    """ Carrega o post pelo respectivo `post_id` """

    post = Post.query.get(post_id)

    if not post:
        response = {
            'title': 'Notícias | FlipNews',
            'message': 'Desculpe, este conteúdo não foi encontrado'
        }
        abort(404, response=response)

    return render_template('news_view_post.html', post=post)


@news_bp.route('/posts/add/', methods=['GET', 'POST'])
@login_required
def add_post():
    """ Cadastrar novas notícias """

    if not current_user.is_admin():
        response = {
            'title': 'Acesso restrito',
            'message': 'Você não tem permissão para acessar essa página'
        }
        abort(403, response=response)

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
                flash('Upload da imagem concluído', category='success')

            post = Post(
                title=post_title,
                text=post_text,
                created_at=post_created_at,
                image_name=post_image_name,
                author_id=current_user.get_id()
            )

            db.session.add(post)
            db.session.commit()

            send_email(post_title)

            flash('Notícia postada com sucesso', category='success')
            return redirect(url_for('.add_post'))

        else:
            logging.warn(f'ERRORS: {post_form.errors}')

    return render_template('news_edit_post.html',
                           post_form=post_form,
                           page_title="Nova notícia | FlipNews")


@news_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
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
                        flash('Upload da nova imagem concluído',
                              category='success')

                        del_command = 'rm' if platform == 'linux' else 'del'
                        img_dest = app.config["UPLOADED_NEWS_IMAGES_DEST"]
                        system(f'{del_command} {img_dest}/{image_name}')

                    db.session.commit()

                    flash('Notícia atualizada com sucesso', category='success')
                else:
                    logging.warn(f'ERRORS: {post_form.errors}')

    else:
        response = {
            'title': 'Notícias | FlipNews',
            'message': 'Desculpe, este conteúdo não foi encontrado'
        }
        abort(404, response=response)

    return render_template('news_edit_post.html',
                           post_form=post_form,
                           image_name=post.image_name,
                           page_title="Editar Notícia | FlipNews",
                           form_action=url_for('.update_post',
                                               post_id=post.post_id))


@news_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """ Apaga a notícia pelo seu `post_id` """

    post = Post.query.get(post_id)

    if post:

        db.session.delete(post)
        db.session.commit()

        if post.image_name is not None:
            del_command = 'rm' if platform == 'linux' else 'del'
            img_dest = app.config["UPLOADED_NEWS_IMAGES_DEST"]
            system(f'{del_command} {img_dest}/{post.image_name}')

        flash('Notícia apagada com sucesso', category='success')
    else:
        flash('Erro ao apagar a notícia', category='warning')

    return redirect(url_for('.show_posts'))
