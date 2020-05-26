from flask import (
    Blueprint, url_for, redirect, render_template, current_app as app
)
from flask_login import current_user

main_bp = Blueprint('main_bp', __name__,
                    template_folder='../templates',
                    static_folder='../static')


@main_bp.route('/')
def index():
    return redirect(url_for('news_bp.show_posts'))
