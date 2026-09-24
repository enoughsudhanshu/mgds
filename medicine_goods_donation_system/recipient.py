from flask import Blueprint, render_template
from flask_login import login_required, current_user

recipient = Blueprint('recipient', __name__, url_prefix='/recipient')

@recipient.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ['ngo', 'hospital']:
        return "Access Denied - You are not NGO/Hospital", 403
    return render_template('recipient/dashboard.html', user=current_user)