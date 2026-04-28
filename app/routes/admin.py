from flask import Blueprint

bp=Blueprint('admin', __name__)

@bp.route('/admin')
def dashboard():
    return "پنل ادمین"