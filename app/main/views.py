from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, \
flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileAdminForm, EditProfileForm, CreateQuizForm
from .. import db
from ..models import User, Role, Permission, Quiz
from ..decorators import admin_required, permission_required

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

''' Quiz operations views '''
@main.route('/quiz')
@login_required
def show_quiz_list():
    form = None
    if current_user.is_administrator():
        quiz_list = Quiz.query.all()
    else:
        quiz_list = current_user.quiz_list.all()
    if current_user.can(Permission.MANAGE_QUIZ):
        form = CreateQuizForm()
    return render_template('quiz_list.html', quiz_list = quiz_list, form = form)

@main.route('/add-quiz', methods = ['POST'])
@login_required
@permission_required(Permission.MANAGE_QUIZ)
def add_quiz():
    form = CreateQuizForm()
    user = User.query.get(current_user.id)
    if form.validate_on_submit():
        quiz = Quiz()
        quiz.title = form.title.data
        quiz.executives.append(user)
        db.session.add(quiz)
        flash('Quiz "%s" succsessfully created.' % quiz.title)
        return redirect(url_for('main.show_quiz_list'))