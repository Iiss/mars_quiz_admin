from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
ValidationError, SelectField, HiddenField
from wtforms.validators import Required, Email, Length
from ..models import User, Role
from urlparse import urlparse, urljoin
from flask import request, redirect, url_for

def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url,target))
	return test_url.scheme in ('http', 'https') and \
		ref_url.netloc == test_url.netloc

class EditProfileAdminForm(Form):
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	name = StringField('Name', validators = [Required(), Length(1, 64)])
	surname = StringField('Surname', validators = [Required(),Length(1,64)])
	role = SelectField('Role', coerce = int)
	phone_number = StringField('Phone', validators = [Length(0, 64)])
	organization = StringField('Organization', validators = [Length(0, 64)])
	submit = SubmitField('Submit')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name)
							for role in Role.query.order_by(Role.name).all()]
		self.user = user
		
	def validate_email(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email = field.data).first():
			raise ValidationError('Email is already registered')

class EditProfileForm(Form):
	phone_number = StringField('Phone', validators = [Length(0, 64)])
	organization = StringField('Organization', validators = [Length(0, 64)])
	submit = SubmitField('Submit')

class ConfirmByPasswordForm(Form):
	submit_field = 'Submit'
	redirect_url = HiddenField()
	password = PasswordField('Password', validators = [Required()])
	submit = SubmitField(submit_field)

	def validate_password(self,field):
		if not current_user.verify_password(field.data):
			raise ValidationError('Invalid password')

	def redirect(self,endpoint='/',**kwargs):
		if is_safe_url(self.next.data):
			return redirect(self.next.data)
		return redirect(url_for(endpoint, **kwargs))



