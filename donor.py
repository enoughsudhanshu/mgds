import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, DonationItem
from datetime import datetime

donor = Blueprint('donor', __name__, url_prefix='/donor')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@donor.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'donor':
        return "Access Denied", 403
    
    # Is donor ke saare items fetch karo
    my_items = DonationItem.query.filter_by(donor_id=current_user.user_id).order_by(DonationItem.created_at.desc()).all()
    return render_template('donor/dashboard.html', user=current_user, items=my_items)


@donor.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role != 'donor':
        return "Access Denied", 403

    if request.method == 'POST':
        item_name = request.form.get('item_name')
        category = request.form.get('category')
        expiry_date_str = request.form.get('expiry_date')
        image = request.files.get('image')

        # Expiry date ko Python date object me convert karo (agar diya ho)
        expiry_date = None
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

        # Image handle karo
        image_path = None
        if image and image.filename != '' and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            # Unique naam banao taaki 2 users same filename se overwrite na karein
            unique_filename = f"{current_user.user_id}_{datetime.utcnow().timestamp()}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(save_path)
            image_path = unique_filename  # DB me sirf filename store karenge

        new_item = DonationItem(
            donor_id=current_user.user_id,
            item_name=item_name,
            category=category,
            expiry_date=expiry_date,
            image_path=image_path,
            status='pending'
        )
        db.session.add(new_item)
        db.session.commit()

        flash('Item listed successfully! Waiting for admin verification.', 'success')
        return redirect(url_for('donor.dashboard'))

    return render_template('donor/add_item.html')

@donor.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if current_user.role != 'donor':
        return "Access Denied", 403

    item = DonationItem.query.get_or_404(item_id)

    # Security check: yeh item isi donor ka hona chahiye
    if item.donor_id != current_user.user_id:
        flash("You can't edit this item.", 'danger')
        return redirect(url_for('donor.dashboard'))

    # Sirf pending items edit ho sakte hain
    if item.status != 'pending':
        flash("Cannot edit item that is already verified/claimed.", 'warning')
        return redirect(url_for('donor.dashboard'))

    if request.method == 'POST':
        item.item_name = request.form.get('item_name')
        item.category = request.form.get('category')
        expiry_date_str = request.form.get('expiry_date')
        item.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date() if expiry_date_str else None

        # Agar nayi image upload ki hai, purani replace karo
        image = request.files.get('image')
        if image and image.filename != '' and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_filename = f"{current_user.user_id}_{datetime.utcnow().timestamp()}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(save_path)
            item.image_path = unique_filename

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('donor.dashboard'))

    return render_template('donor/edit_item.html', item=item)


@donor.route('/delete-item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if current_user.role != 'donor':
        return "Access Denied", 403

    item = DonationItem.query.get_or_404(item_id)

    if item.donor_id != current_user.user_id:
        flash("You can't delete this item.", 'danger')
        return redirect(url_for('donor.dashboard'))

    if item.status != 'pending':
        flash("Cannot delete item that is already verified/claimed.", 'warning')
        return redirect(url_for('donor.dashboard'))

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('donor.dashboard'))