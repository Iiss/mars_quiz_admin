from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, \
flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileAdminForm, EditProfileForm
from .. import db
from ..models import User, Role
from ..decorators import admin_required

@main.route('/',methods=['GET','POST'])
def index():
    user_list = User.query.all()
    return render_template("index.html", user_list = user_list)

@main.route('/user/<int:id>')
def show_profile(id):
    user = User.query.filter_by(id = id).first()
    if user is None:
        abort(404)
    return render_template("user.html", user = user)

@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    form = EditProfileForm()
    if form.validate_on_submit():
        user.phone_number = form.phone_number.data
        user.organization = form.organization.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('main.show_profile',id = user.id))
    form.phone_number.data = user.phone_number
    form.organization.data = user.organization
    return render_template('edit_profile.html', form = form, user = user)

@main.route('/edit-profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.role = Role.query.get(form.role.data)
        user.phone_number = form.phone_number.data
        user.organization = form.organization.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('main.show_profile',id = user.id))
    form.email.data = user.email
    form.name.data = user.name
    form.surname.data = user.surname
    form.role.data = user.role_id
    form.phone_number.data = user.phone_number
    form.organization.data = user.organization
    return render_template('edit_profile.html', form = form, user = user)