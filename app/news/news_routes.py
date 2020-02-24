from flask import Blueprint, render_template, request

from flask_login import (
    login_required, current_user
)

news_bp = Blueprint('news_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/news')


@news_bp.route('/', methods=['GET'])
def index():
    """ Rota de notícias """
    return render_template('news.html')
