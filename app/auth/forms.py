# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User

class  LoginForm(Form):
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators = [Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

class AddUserForm(Form):
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	name = StringField(u'Имя', validators = [Required(), Length(1, 64)])
	surname = StringField(u'Фамилия', validators = [Required(),Length(1,64)])
	submit = SubmitField(u'Отправить приглашение')

	def validate_email(self, field):
		user = User.query.filter_by(email = field.data).first()
		if user and user.confirmed:
			raise ValidationError('Email already registered')

class RegistrationForm(Form):
	password = PasswordField('Password', validators = [
		Required(), EqualTo('password2', message = 'Passwords must match.')])
	password2 = PasswordField('Confirm password', validators = [Required()])
	submit = SubmitField('Register')

class ChangePasswordForm(Form):
	old_password = PasswordField('Old password', validators = [Required()])
	password = PasswordField('New password', validators = [
		Required(), EqualTo('password2', message = 'Passwords must match.')])
	password2 = PasswordField('Confirm new password', validators = [Required()])
	submit = SubmitField('Update Password')

class PasswordResetRequestForm(Form):
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	submit = SubmitField('Reset Password')

class PasswordResetForm(Form):
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators = [
		Required(), EqualTo('password2', message = 'Passwords must match.')])
	password2 = PasswordField('Confirm password', validators = [Required()])
	submit = SubmitField('Reset Password')

	def validate_email(self, field):
		if User.query.filter_by(email = field.data).first() is None:
			raise ValidationError('Unknown Email Address')

class ChangeEmailForm(Form):
	email = StringField('New Email', validators = [Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators = [Required()])
	submit = SubmitField('Reset Password')

	def validate_email(self, field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email is already registered')
		