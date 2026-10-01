from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Access Denied - You are not admin", 403
    return render_template('admin/dashboard.html', user=current_user)