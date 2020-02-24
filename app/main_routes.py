from flask import render_template, Blueprint

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
    return render_template('main_index.html')
