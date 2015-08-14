import unittest
from app.models import User, AnonymousUser, Role, Permission
from flask import current_app
from app import db
import time

class UserModelTestCase(unittest.TestCase):

	def test_password_setter(self):
		u = User(password = 'cat')
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = User(password = 'cat')
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u = User(password = 'cat')
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_salts_are_random(self):
		u = User(password = 'cat')
		u2 = User(password = 'cat')
		self.assertTrue(u.password_hash != u2.password_hash)

	def test_valid_confirmation_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token()
		self.assertTrue(User.parse_invite_token(token))

	def test_expired_confirmation_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token(1)
		time.sleep(2)
		self.assertFalse(User.parse_invite_token(token))

	def test_valid_reset_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_reset_token()
		self.assertTrue(u.reset_password(token,'dog'))
		self.assertTrue(u.verify_password('dog'))

	def test_invalid_reset_token(self):
		u1 = User(password = 'cat')
		u2 = User(password = 'dog')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		token = u1.generate_reset_token()
		self.assertFalse(u2.reset_password(token,'horse'))
		self.assertTrue(u2.verify_password('dog'))

	def test_expired_reset_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_reset_token(1)
		time.sleep(2)
		self.assertFalse(u.reset_password(token,'dog'))
		self.assertFalse(u.verify_password('dog'))
	
	def test_valid_email_change_token(self):
		u = User(email = 'olddog@example.com', password = 'dog')
		db.session.add(u)
		db.session.commit()
		token = u.generate_email_change_token('newdog@example.com')
		self.assertTrue(u.change_email(token))
		self.assertTrue(u.email == 'newdog@example.com')

	def test_expired_email_change_token(self):
		u = User(email = 'cat@example.com', password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_email_change_token('newcat@example.com',1)
		time.sleep(2)
		self.assertFalse(u.change_email('newcat@example.com'))
		self.assertTrue(u.email == 'cat@example.com')

	def test_roles_and_permissions(self):
		Role.insert_roles()
		u = User(email = 'john@example.com', password = 'cat')
		self.assertTrue(u.can(Permission.WRITE_ARTICLES))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))

	def test_admin_auto_set(self):
		Role.insert_roles()
		admin_email = current_app.config['FLASKY_ADMIN']
		other_email = 'fake%r' % admin_email
		u1 = User(email = admin_email)
		u2 = User(email = other_email)
		self.assertTrue(u1.is_administrator())
		self.assertFalse(u2.is_administrator())
