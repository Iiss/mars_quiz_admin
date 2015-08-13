from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
ValidationError, SelectField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User, Role
		
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